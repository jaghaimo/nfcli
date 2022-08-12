using System;
using UnityEngine;

public class LogHandler : ILogHandler
{
    public void LogFormat(LogType logType, UnityEngine.Object context, string format, params object[] args)
    {
        Console.WriteLine(format, args);
    }

    public void LogException(Exception exception, UnityEngine.Object context)
    {
        Console.WriteLine(exception.ToString());
    }
}