import os
import matplotlib.pyplot as plt


def save_plot(fig_path: str):
    '''
    This method will save an already
    loaded plot into the specified path.

    Example:
    ```
    plt.scatter(1, 1)
    save_plot("lmao/hey.png")
    ```

    :param fig_path: Desired path for the
    figure.
    '''
    os.makedirs(
        os.path.dirname(fig_path),
        exist_ok=True
    )

    plt.savefig(fig_path)
    plt.close()
