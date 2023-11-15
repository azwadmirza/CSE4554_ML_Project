def sign(x):
  r"""Elementwise sign.

  For floating-point inputs, returns
  :math:`\mathrm{sign}(x) = \begin{cases}
  -1 & x < 0\\
  -0 & x = -0\\
  \mathit{NaN} & x = \mathit{NaN}\\
  +0 & x = +0\\
  1 & x > 0
  \end{cases}`

  For signed integer inputs, returns
  :math:`\mathrm{sign}(x) = \begin{cases}
  -1 & x < 0\\
  0 & x = 0\\
  1 & x > 0
  \end{cases}`

  For complex inputs, returns the complex phase, i.e.
  :math:`\mathrm{sign}(x) = \frac{x}{|x|}`.
  """
  return sign_p.bind(x)