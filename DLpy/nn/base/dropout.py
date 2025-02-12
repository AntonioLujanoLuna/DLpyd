from typing import Any, Optional

import numpy as np
from numpy.typing import NDArray

from ...core import Module, Tensor


class Dropout(Module):
    """
    Randomly zeroes some elements of the input tensor with probability p.

    Args:
        p (float): Probability of an element to be zeroed. Default: 0.5
        inplace (bool): If True, will do operation in-place. Default: False
    """

    def __init__(self, p: float = 0.5, inplace: bool = False):
        super().__init__()
        if p < 0 or p > 1:
            raise ValueError(
                f"dropout probability has to be between 0 and 1, but got {p}"
            )
        self.p = p
        self.inplace = inplace

    def forward(self, x: Tensor) -> Tensor:
        """
        Forward pass of dropout.

        Args:
            x: Input tensor

        Returns:
            Output tensor, either the same object (if inplace=True) or a new tensor
        """
        if self.training:
            # Generate random mask
            mask = (np.random.rand(*x.shape) > self.p).astype(np.float64)
            # Scale up to maintain expected value
            scale = 1.0 / (1.0 - self.p) if self.p != 1.0 else 0.0
            mask = mask * scale

            if self.inplace:
                # Modify input tensor directly
                x.data *= mask
                return x
            else:
                # Create new tensor
                return Tensor(x.data * mask, requires_grad=x.requires_grad)
        return x


class Dropout2d(Module):
    """
    Randomly zero out entire channels (a channel is a 2D feature map,
    e.g., the j-th channel of the i-th sample in the batch input) of the input tensor.
    Each channel will be zeroed out independently on every forward call
    with probability p.

    Args:
        p: Probability of a channel to be zeroed. Default: 0.5
        inplace: If set to True, will do operation in-place. Default: False
    """

    def __init__(self, p: float = 0.5, inplace: bool = False):
        super().__init__()
        if p < 0 or p > 1:
            raise ValueError(
                f"dropout probability has to be between 0 and 1, but got {p}"
            )
        self.p = p
        self.inplace = inplace
        self.mask: Optional[NDArray[Any]] = None

    def forward(self, x: Tensor) -> Tensor:
        if self.training:
            assert len(x.shape) == 4, f"expected 4D input, got {len(x.shape)}D input"

            # Generate mask for entire channels
            mask = (np.random.rand(x.shape[0], x.shape[1], 1, 1) > self.p).astype(
                np.float64
            )
            self.mask = np.broadcast_to(mask, x.shape)

            # Scale up by 1/(1-p) to maintain expected value
            scale = 1.0 / (1.0 - self.p) if self.p != 1.0 else 0.0

            if self.inplace:
                x.data *= self.mask * scale
                return x
            else:
                return Tensor(x.data * self.mask * scale, requires_grad=x.requires_grad)
        else:
            return x
