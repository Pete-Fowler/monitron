using System.ComponentModel;
using Avalonia.Controls;

namespace MonitronApp;

public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
        Closing += OnClosingHide;
    }

    private void OnClosingHide(object? sender, CancelEventArgs e)
    {
        // Keep the app running and hide the window instead of closing.
        e.Cancel = true;
        Hide();
    }
}