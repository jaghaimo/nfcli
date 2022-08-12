using System;
using System.IO;
using Networking;
using System.Net;
using System.Threading;
using UnityEngine;

class LobbyPoller
{
    private static MultiplayerFilters _filters = default;
    private static string? _discordHook = null;

    public void Start()
    {

        LoadToken();
        LobbyPoll();
    }

    private void LoadToken()
    {
        var filePath = "LobbyPoller.txt";
        if (!File.Exists(filePath))
        {
            Console.WriteLine($"Missing config file {filePath}");
            return;
        }
        var content = File.ReadAllText(filePath);
        _discordHook = content.Trim();
    }
    private void LobbyPoll()
    {
        while (true)
        {
            SteamLobbyList lobbyList = new SteamLobbyList();
            lobbyList.RefreshLobbies(_filters);
            if (lobbyList.Status == MatchListRefreshStatus.Failed)
            {
                Debug.Log("Failed to refresh lobbies!");
                Thread.Sleep(10000);
                continue;
            }
            while (lobbyList.Status == MatchListRefreshStatus.Refreshing)
            {
                Thread.Sleep(500);
                lobbyList.GetNewLobbies();
            }
            Debug.Log($"Lobbies refreshed, found {lobbyList.AllLobbies.Count}");
            SendData(lobbyList);
            Thread.Sleep(60000);
        }
    }

    private void SendData(SteamLobbyList lobbyList)
    {
        var parameters = new System.Collections.Specialized.NameValueCollection
            {
                { "content", GetLobbyData(lobbyList) }
            };
        using (WebClient wc = new WebClient())
        {
            wc.UploadValues(_discordHook, parameters);
        }
    }

    /**
      * Returns partial JSON string with lobby data, e.g.
      * [{"h":0,"i":1},{"h":1,"i":0}]
      */
    private string GetLobbyData(SteamLobbyList lobbyList)
    {
        string lobbies = "";
        foreach (SteamLobby lobby in lobbyList.AllLobbies)
        {
            string lobbyData = "{";
            lobbyData += AddField("h", lobby.HasPassword ? 1 : 0);
            lobbyData += AddField("i", lobby.InProgress ? 1 : 0);
            lobbies += lobbyData.TrimEnd(',') + "},";
        }
        return "[" + lobbies.TrimEnd(',') + "]";
    }

    /**
     * Returns JSON encoded int field with a trailing comma, e.g.
     * "h":0,
     */
    private string AddField(string key, int value)
    {
        return $"\"{key}\":{value},";
    }
}