"""自定义异常"""


class BaseAPIException(Exception):
    """API基础异常"""
    def __init__(self, message: str = "操作失败", code: int = 400):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundException(BaseAPIException):
    """资源未找到异常"""
    def __init__(self, message: str = "资源未找到"):
        super().__init__(message=message, code=404)


class ValidationException(BaseAPIException):
    """数据验证异常"""
    def __init__(self, message: str = "数据验证失败"):
        super().__init__(message=message, code=422)


class PermissionException(BaseAPIException):
    """权限异常"""
    def __init__(self, message: str = "权限不足"):
        super().__init__(message=message, code=403)


class FileUploadException(BaseAPIException):
    """文件上传异常"""
    def __init__(self, message: str = "文件上传失败"):
        super().__init__(message=message, code=400)

