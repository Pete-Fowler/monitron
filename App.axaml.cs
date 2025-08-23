using System;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;

namespace MonitronApp;

public partial class App : Application
{
    private TrayIcon? _tray;

    public override void Initialize() => AvaloniaXamlLoader.Load(this);

    public override void OnFrameworkInitializationCompleted()
    {
        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            var main = new MainWindow();

            // main.Icon =

            desktop.MainWindow = main;

            try
            {
                _tray = new TrayIcon
                {
                    Icon = new WindowIcon("/Assets/monitor32.png"),
                    ToolTipText = "Monitron",
                    Menu = new NativeMenu(),
                };

                var showItem = new NativeMenuItem("Show");
                showItem.Click += (_, __) =>
                {
                    if (desktop.MainWindow is Window w)
                    {
                        w.Show();
                        w.Activate();
                    }
                };

                var quitItem = new NativeMenuItem("Quit");
                quitItem.Click += (_, __) => desktop.Shutdown();

                _tray.Menu.Items.Add(showItem);
                _tray.Menu.Items.Add(new NativeMenuItemSeparator());
                _tray.Menu.Items.Add(quitItem);

                _tray.IsVisible = true;
            }
            catch (Exception ex)
            {
                // If creating a TrayIcon fails, continue without it.
                // On modern GNOME Wayland you may need libayatana-appindicator3-1 for the icon to appear.
                Console.Error.WriteLine($"Tray icon creation failed: {ex}");
            }
        }

        base.OnFrameworkInitializationCompleted();
    }
}