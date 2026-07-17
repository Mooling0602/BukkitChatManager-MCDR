import hashlib
import os
import re
import threading
import time
from dataclasses import dataclass
from urllib.request import urlopen

import psutil
from mcdreforged.api.all import new_thread, spam_proof
from mcdreforged.command.command_source import CommandSource
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

import bkchat_manager.runtime as rt


PLAYERLOG_VERSION = "2.0"
PLAYERLOG_DOWNLOAD_URL = "https://github.com/Mooling0602/PlayerLog-Bukkit/releases/download/2.0/PlayerLog-2.0.jar"
PLAYERLOG_FILE_NAME = "PlayerLog-2.0.jar"


@dataclass
class DownloadStatus:
    active: bool = False
    completed: bool = False
    error: str | None = None
    downloaded_size: int = 0
    total_size: int | None = None
    started_at: float | None = None
    destination: str | None = None
    task_id: int = 0


@dataclass(frozen=True)
class PluginPackage:
    path: str
    version: Version | None


class PluginPackageBackupError(Exception):
    pass


_download_lock = threading.Lock()
_download_status = DownloadStatus()


def _resolve_directory(directory: str) -> str:
    return os.path.abspath(os.path.expanduser(directory))


def _is_server_directory(directory: str) -> bool:
    return os.path.isdir(directory) and os.path.isdir(
        os.path.join(directory, "plugins")
    )


def _warn_if_directory_confidence_is_low(server_directory: str) -> None:
    server_properties = os.path.join(server_directory, "server.properties")
    plugin_directory = os.path.join(server_directory, "plugins")
    reasons = []

    try:
        server_properties_missing_or_empty = (
            not os.path.isfile(server_properties)
            or os.path.getsize(server_properties) == 0
        )
    except OSError:
        server_properties_missing_or_empty = True

    if server_properties_missing_or_empty:
        reasons.append("server.properties 不存在或为空")

    try:
        with os.scandir(plugin_directory) as entries:
            if not any(entries):
                reasons.append("plugins 文件夹为空")
    except OSError:
        reasons.append("无法读取 plugins 文件夹内容")

    if reasons:
        rt.psi.logger.warning(
            "获取到的服务端目录位置置信度较低：%s（%s）",
            server_directory,
            "；".join(reasons),
        )


def _get_server_process_directory() -> str | None:
    server_pid = rt.psi.get_server_pid()
    if not isinstance(server_pid, int):
        rt.psi.logger.warning("服务端进程未运行，无法通过 PID 定位服务端目录。")
        return None

    try:
        return _resolve_directory(psutil.Process(server_pid).cwd())
    except (OSError, psutil.Error) as error:
        rt.psi.logger.warning("无法获取服务端进程 %s 的工作目录：%s", server_pid, error)
        return None


def get_server_directory() -> str | None:
    configured_directory = _resolve_directory(
        rt.psi.get_mcdr_config().get("working_directory", "server")
    )
    if _is_server_directory(configured_directory):
        _warn_if_directory_confidence_is_low(configured_directory)
        return configured_directory

    rt.psi.logger.warning(
        "MCDR working_directory %s 不是有效的 Bukkit 服务端目录，正在尝试通过服务端 PID 定位。",
        configured_directory,
    )
    process_directory = _get_server_process_directory()
    if process_directory is not None and _is_server_directory(process_directory):
        _warn_if_directory_confidence_is_low(process_directory)
        return process_directory

    if process_directory is not None:
        rt.psi.logger.warning(
            "服务端进程工作目录 %s 不是有效的 Bukkit 服务端目录。",
            process_directory,
        )
    rt.psi.logger.error(
        "无法定位 Bukkit 服务端目录；请手动安装 PlayerLog %s，或在 BukkitChatManager 配置中提供正确的服务端目录位置（该配置项尚未实现）。",
        PLAYERLOG_VERSION,
    )
    return None


def _get_plugin_name_pattern() -> re.Pattern | None:
    try:
        return re.compile(rt.config.bukkit_plugin_management.file_name_regex)
    except re.error as error:
        rt.psi.logger.error("Bukkit 插件文件名正则无效：%s", error)
        return None


def _get_plugin_version(match: re.Match, file_name: str) -> Version | None:
    version_text = match.groupdict().get("version")
    if version_text is None and match.lastindex:
        version_text = match.group(1)
    if version_text is None:
        return None

    try:
        return Version(version_text)
    except InvalidVersion:
        rt.psi.logger.warning("无法从 Bukkit 插件包 %s 解析版本 %s。", file_name, version_text)
        return None


def _find_plugin_packages(
    plugin_directory: str, pattern: re.Pattern
) -> list[PluginPackage]:
    packages = []
    try:
        with os.scandir(plugin_directory) as entries:
            for entry in entries:
                if not entry.is_file() or not entry.name.lower().endswith(".jar"):
                    continue
                match = pattern.fullmatch(entry.name)
                if match is not None:
                    packages.append(
                        PluginPackage(
                            path=entry.path,
                            version=_get_plugin_version(match, entry.name),
                        )
                    )
    except OSError as error:
        rt.psi.logger.error("无法扫描 Bukkit 插件目录 %s：%s", plugin_directory, error)
    return packages


def _get_version_limit(version_limit: str) -> SpecifierSet | None:
    if not version_limit:
        return None

    try:
        return SpecifierSet(version_limit)
    except InvalidSpecifier as error:
        rt.psi.logger.error("Bukkit 插件版本限制无效：%s", error)
        return None


def _get_expected_sha256() -> str | None:
    expected_sha256 = rt.config.bukkit_plugin_management.file_sha256.strip().lower()
    if not expected_sha256:
        return None
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        rt.psi.logger.error("Bukkit 插件 SHA-256 配置无效。")
        return None
    return expected_sha256


def _calculate_sha256(file_path: str) -> str:
    digest = hashlib.sha256()
    with open(file_path, "rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _check_plugin_package_hash(
    plugin_path: str, expected_sha256: str | None
) -> bool:
    if expected_sha256 is None:
        return True

    try:
        actual_sha256 = _calculate_sha256(plugin_path)
    except OSError as error:
        rt.psi.logger.warning("无法计算 Bukkit 插件包 SHA-256 %s：%s", plugin_path, error)
        return False

    if actual_sha256 == expected_sha256:
        return True

    rt.psi.logger.warning("Bukkit 插件包 SHA-256 不匹配：%s", plugin_path)
    return False


def _backup_plugin_package(plugin_path: str) -> bool:
    backup_path = f"{plugin_path}.bak"
    index = 1
    while os.path.exists(backup_path):
        backup_path = f"{plugin_path}.{index}.bak"
        index += 1

    try:
        os.rename(plugin_path, backup_path)
    except OSError as error:
        rt.psi.logger.error("无法备份 SHA-256 不匹配的 Bukkit 插件包 %s：%s", plugin_path, error)
        return False

    rt.psi.logger.warning(
        "Bukkit 插件包 SHA-256 不匹配，已备份至 %s。", backup_path
    )
    return True


def _find_usable_plugin_package(
    plugin_directory: str,
    pattern: re.Pattern,
    version_limit: SpecifierSet | None,
    expected_sha256: str | None,
) -> PluginPackage | None:
    force_hash_check = rt.config.bukkit_plugin_management.force_hash_check

    for package in _find_plugin_packages(plugin_directory, pattern):
        if version_limit is not None:
            if package.version is None:
                rt.psi.logger.warning("无法确认 Bukkit 插件包版本：%s", package.path)
                continue
            if package.version not in version_limit:
                rt.psi.logger.info(
                    "Bukkit 插件包 %s 版本 %s 不符合要求 %s。",
                    package.path,
                    package.version,
                    version_limit,
                )
                continue

        if not _check_plugin_package_hash(package.path, expected_sha256):
            if force_hash_check:
                if not _backup_plugin_package(package.path):
                    raise PluginPackageBackupError(package.path)
                continue

        return package

    return None


def _format_size(size: int) -> str:
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


def _format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{max(1, round(seconds))} 秒"
    minutes, seconds = divmod(round(seconds), 60)
    if minutes < 60:
        return f"{minutes} 分 {seconds} 秒"
    hours, minutes = divmod(minutes, 60)
    return f"{hours} 时 {minutes} 分"


def _get_download_status_message() -> str:
    with _download_lock:
        status = DownloadStatus(**_download_status.__dict__)

    if status.active and status.started_at is not None:
        elapsed = max(time.monotonic() - status.started_at, 0.001)
        speed = status.downloaded_size / elapsed
        downloaded = _format_size(status.downloaded_size)
        speed_text = f"{_format_size(round(speed))}/s"

        if status.total_size is None or status.total_size <= 0:
            return f"正在下载 PlayerLog {PLAYERLOG_VERSION}：{downloaded}，速度 {speed_text}，预计剩余时间未知"

        progress = status.downloaded_size / status.total_size * 100
        remaining = max(status.total_size - status.downloaded_size, 0)
        eta_text = _format_duration(remaining / speed) if speed > 0 else "未知"
        return (
            f"正在下载 PlayerLog {PLAYERLOG_VERSION}：{downloaded} / "
            f"{_format_size(status.total_size)} ({progress:.1f}%)，"
            f"速度 {speed_text}，预计剩余时间 {eta_text}"
        )

    if status.completed and status.destination is not None:
        return f"PlayerLog {PLAYERLOG_VERSION} 已下载至 {status.destination}。"
    if status.error is not None:
        return f"PlayerLog {PLAYERLOG_VERSION} 下载失败：{status.error}"
    return "当前没有 PlayerLog 下载任务。"


def on_download_status_command(source: CommandSource) -> None:
    source.reply(_get_download_status_message())


def _on_duplicate_download(destination: str) -> None:
    rt.psi.logger.warning("PlayerLog 下载任务已在进行中：%s", destination)


@new_thread("BukkitChatManager:PlayerLogDownload")
@spam_proof(skip_callback=_on_duplicate_download)
def _download_playerlog(destination: str) -> None:
    temporary_path = f"{destination}.part"

    try:
        with urlopen(PLAYERLOG_DOWNLOAD_URL, timeout=30) as response, open(
            temporary_path, "wb"
        ) as output:
            content_length = response.headers.get("Content-Length")
            try:
                total_size = int(content_length) if content_length is not None else None
            except ValueError:
                total_size = None
            with _download_lock:
                _download_status.total_size = total_size

            while chunk := response.read(1024 * 256):
                output.write(chunk)
                with _download_lock:
                    _download_status.downloaded_size += len(chunk)

        expected_sha256 = _get_expected_sha256()
        if not _check_plugin_package_hash(temporary_path, expected_sha256):
            if rt.config.bukkit_plugin_management.force_hash_check:
                raise ValueError("下载的 Bukkit 插件包 SHA-256 不匹配")

        os.replace(temporary_path, destination)
        with _download_lock:
            _download_status.active = False
            _download_status.completed = True
        rt.psi.logger.info(_get_download_status_message())
        rt.psi.logger.warning(
            "PlayerLog %s 下载完成，请重启服务端以加载 Bukkit 插件。",
            PLAYERLOG_VERSION,
        )
    except Exception as error:
        try:
            os.remove(temporary_path)
        except OSError:
            pass

        with _download_lock:
            _download_status.active = False
            _download_status.error = str(error)
        rt.psi.logger.error(_get_download_status_message())


@new_thread("BukkitChatManager:PlayerLogDownloadProgress")
def _report_download_progress(task_id: int) -> None:
    while True:
        time.sleep(1)
        with _download_lock:
            if not _download_status.active or _download_status.task_id != task_id:
                return
        rt.psi.logger.info(_get_download_status_message())


def download_playerlog_plugin(server_directory: str) -> bool:
    destination = os.path.join(server_directory, "plugins", PLAYERLOG_FILE_NAME)

    with _download_lock:
        if _download_status.active:
            rt.psi.logger.warning("PlayerLog 下载任务已在进行中。")
            return False

        _download_status.active = True
        _download_status.completed = False
        _download_status.error = None
        _download_status.downloaded_size = 0
        _download_status.total_size = None
        _download_status.started_at = time.monotonic()
        _download_status.destination = destination
        _download_status.task_id += 1
        task_id = _download_status.task_id

    rt.psi.logger.info("开始下载 PlayerLog %s：%s", PLAYERLOG_VERSION, destination)
    _report_download_progress(task_id)
    _download_playerlog(destination)
    return True


def install_bukkit_plugin() -> bool:
    server_directory = get_server_directory()
    if server_directory is None:
        return False

    pattern = _get_plugin_name_pattern()
    if pattern is None:
        rt.psi.logger.error("Bukkit 插件文件名正则无效，已取消自动安装。")
        return False

    version_limit_text = rt.config.bukkit_plugin_version_limit.strip()
    version_limit = _get_version_limit(version_limit_text)
    if version_limit_text and version_limit is None:
        rt.psi.logger.error("Bukkit 插件版本限制无效，已取消自动安装。")
        return False

    expected_sha256 = _get_expected_sha256()
    if rt.config.bukkit_plugin_management.force_hash_check and expected_sha256 is None:
        rt.psi.logger.error("已启用强制 SHA-256 校验，但未提供有效的 SHA-256。")
        return False

    plugin_directory = os.path.join(server_directory, "plugins")
    try:
        package = _find_usable_plugin_package(
            plugin_directory, pattern, version_limit, expected_sha256
        )
    except PluginPackageBackupError as error:
        rt.psi.logger.error(
            "无法备份 SHA-256 不匹配的 Bukkit 插件包 %s，已取消自动安装。",
            error,
        )
        return False
    if package is not None:
        rt.psi.logger.info("已找到可用的 Bukkit 插件包：%s", package.path)
        return True

    download_playerlog_plugin(server_directory)
    return False
