using System;
using System.Reflection;
using Steamworks;
using Networking;
using UnityEngine;

// replace Unity logger
var newLogger = new Logger(new LogHandler());
var fieldInfo = typeof(Debug).GetField("s_Logger", BindingFlags.GetField | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Static);
fieldInfo.SetValue(null, newLogger);

SteamClient.Init(887570);
if (SteamClient.IsValid)
{
    // prepare Steam manager
    var manager = new SteamManager();
    var fieldInstance = typeof(SteamManager).GetField("_instance", BindingFlags.GetField | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Static);
    var fieldInitialized = typeof(SteamManager).GetField("_initialized", BindingFlags.GetField | BindingFlags.Instance | BindingFlags.NonPublic);
    fieldInitialized.SetValue(manager, true);
    fieldInstance.SetValue(null, manager);

    var poller = new LobbyPoller();
    poller.Start();
}
else
{
    Console.WriteLine("Failed to initialize SteamAPI.");
}
