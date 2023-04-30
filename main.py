# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

#ken? date: apr 23, 2023

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    """
    A simple example of an animated plot
    """
    import numpy as np

    import matplotlib ; matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt;
    import matplotlib.animation as animation

    fig, ax = plt.subplots()

    x = np.arange(0, 2 * np.pi, 0.01)
    line, = ax.plot(x, np.sin(x))


    def animate(i):
        line.set_ydata(np.sin(x + i / 10.0))  # update the data
        return line,


    # Init only required for blitting to give a clean slate.
    def init():
        line.set_ydata(np.ma.array(x, mask=True))
        return line,


    ani = animation.FuncAnimation(fig, animate, np.arange(1, 200), init_func=init,
                                  interval=25, blit=True)
    plt.show()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
