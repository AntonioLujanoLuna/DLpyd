from typing import Any, Callable, Dict, Optional, Tuple, Union

import numpy as np
from numpy.typing import NDArray

from ..core import Function, Tensor
from ..core.context import Context  # Make sure to import Context


class Transpose(Function):
    @staticmethod
    def forward(
        ctx: Context,
        x: Union[Tensor, NDArray[Any]],
        axes: Optional[Tuple[int, ...]] = None,
    ) -> Tensor:
        """
        Transposes a tensor along specified axes.

        Args:
            ctx: Context for storing information needed in backward pass
            x: Input tensor to transpose
            axes: Optional tuple specifying the permutation of dimensions

        Returns:
            Transposed tensor
        """
        if not isinstance(x, Tensor):
            x = Tensor(x)

        ctx.save_for_backward(x)
        ctx.save_arguments(axes=axes)

        if axes is None:
            return Tensor(np.transpose(x.data))
        return Tensor(np.transpose(x.data, axes))

    @staticmethod
    def backward(
        ctx: Context, grad_output: NDArray[Any], grad_dict: Dict[int, NDArray[Any]]
    ) -> None:
        (x,) = ctx.saved_tensors
        axes = ctx.saved_arguments["axes"]

        if x.requires_grad:
            if axes is None:
                # For standard transpose, just transpose the gradient
                grad_dict[id(x)] = np.transpose(grad_output)
            else:
                # For specific axes, need to invert the permutation
                inverse_axes = np.argsort(axes)
                grad_dict[id(x)] = np.transpose(grad_output, inverse_axes)


class Compare(Function):
    """Base class for comparison operations"""

    @staticmethod
    def _compare(
        op: Callable[[NDArray[Any], NDArray[Any]], NDArray[bool]],
        x1: Union[Tensor, NDArray[Any], float, int],
        x2: Union[Tensor, NDArray[Any], float, int],
    ) -> Tensor:
        """
        Applies a comparison operation between two tensors.

        Args:
            op: NumPy comparison function to apply
            x1: First tensor or scalar to compare
            x2: Second tensor or scalar to compare

        Returns:
            Boolean tensor containing the comparison results
        """
        if not isinstance(x1, Tensor):
            x1 = Tensor(x1)
        if not isinstance(x2, Tensor):
            x2 = Tensor(x2)

        return Tensor(op(x1.data, x2.data))

    @staticmethod
    def backward(
        ctx: Context, grad_output: NDArray[Any], grad_dict: Dict[int, NDArray[Any]]
    ) -> None:
        """Comparison operations have no gradient"""


class Greater(Compare):
    @staticmethod
    def forward(
        ctx: Context,
        x1: Union[Tensor, NDArray[Any], float, int],
        x2: Union[Tensor, NDArray[Any], float, int],
    ) -> Tensor:
        return Compare._compare(np.greater, x1, x2)


class GreaterEqual(Compare):
    @staticmethod
    def forward(
        ctx: Context,
        x1: Union[Tensor, NDArray[Any], float, int],
        x2: Union[Tensor, NDArray[Any], float, int],
    ) -> Tensor:
        return Compare._compare(np.greater_equal, x1, x2)


class Less(Compare):
    @staticmethod
    def forward(
        ctx: Context,
        x1: Union[Tensor, NDArray[Any], float, int],
        x2: Union[Tensor, NDArray[Any], float, int],
    ) -> Tensor:
        return Compare._compare(np.less, x1, x2)


class LessEqual(Compare):
    @staticmethod
    def forward(
        ctx: Context,
        x1: Union[Tensor, NDArray[Any], float, int],
        x2: Union[Tensor, NDArray[Any], float, int],
    ) -> Tensor:
        return Compare._compare(np.less_equal, x1, x2)


class Equal(Compare):
    @staticmethod
    def forward(
        ctx: Context,
        x1: Union[Tensor, NDArray[Any], float, int],
        x2: Union[Tensor, NDArray[Any], float, int],
    ) -> Tensor:
        return Compare._compare(np.equal, x1, x2)


class NotEqual(Compare):
    @staticmethod
    def forward(
        ctx: Context,
        x1: Union[Tensor, NDArray[Any], float, int],
        x2: Union[Tensor, NDArray[Any], float, int],
    ) -> Tensor:
        return Compare._compare(np.not_equal, x1, x2)
