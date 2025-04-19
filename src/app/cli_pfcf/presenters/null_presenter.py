from typing import Any, Dict


class NullPresenter:
    """A universal null presenter that implements all presenter interfaces."""
    
    def present(self, output_dto: Any) -> Dict:
        """Present any output DTO by returning a minimal dictionary."""
        # 基本信息
        result = {
            "action": "background_operation",
            "success": True,
            "message": "Operation completed in background mode"
        }
        
        # 尝试提取 DTO 中的有用属性
        try:
            for attr in dir(output_dto):
                if not attr.startswith('_') and not callable(getattr(output_dto, attr)):
                    result[attr] = getattr(output_dto, attr)
        except (AttributeError, TypeError):
            pass
            
        return result