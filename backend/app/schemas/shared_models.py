from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel

# 为了避免循环导入，我们在这里定义所有需要相互引用的模型

if TYPE_CHECKING:
    from .photogroup import PhotoGroup
    from .analysis_result import AnalysisResult

# 这个文件的主要目的是提供一个共享的模型定义空间，
# 避免在photogroup.py和analysis_result.py之间直接相互导入