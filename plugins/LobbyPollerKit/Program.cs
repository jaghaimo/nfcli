using System;
using Steamworks;

SteamClient.Init(877570);
if (SteamClient.IsValid)
{
    Console.WriteLine("Hello, World! Steam connected.");
}
else
{
    Console.WriteLine("Not Hello, World! Steam failed.");
}