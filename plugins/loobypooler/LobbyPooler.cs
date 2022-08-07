using Modding;
using Networking;
using System.Net;
using System.Threading;
using UnityEngine;

namespace LobbyPooler
{
    public class LobbyPooler : IModEntryPoint
    {
        private static MultiplayerFilters _filters = default;

        public void PostLoad()
        {
            _filters.HideInProgress = false;
            _filters.HidePassword = false;
            Thread thread = new Thread(new ThreadStart(LobbyPool));
            thread.Start();
        }

        public void PreLoad()
        {
        }

        private void LobbyPool()
        {
            while (true)
            {
                if (!SteamManager.Initialized)
                {
                    Debug.Log("We are too early!");
                    return;
                }
                SteamLobbyList lobbyList = new SteamLobbyList();
                lobbyList.RefreshLobbies(_filters);
                if (lobbyList.Status == MatchListRefreshStatus.Failed)
                {
                    Debug.Log("Failed to refresh lobbies!");
                    return;
                }
                while (lobbyList.Status == MatchListRefreshStatus.Refreshing)
                {
                    Thread.Sleep(1000);
                    Debug.Log("Fetching new lobbies");
                    lobbyList.GetNewLobbies();
                }
                Debug.Log($"Lobbies refreshed, found {lobbyList.AllLobbies.Count} lobbies");
                foreach (SteamLobby steamLobby in lobbyList.AllLobbies)
                {
                    Debug.Log($"{steamLobby.Name} - {steamLobby.CurrentPlayers} / {steamLobby.MaxPlayers}");
                }
                SendData(lobbyList);
                Thread.Sleep(60000);
            }
        }

        private void SendData(SteamLobbyList lobbyList)
        {
            string uri = "https://discord.com/api/webhooks/1005583148698046515/qHx3Lbkg8TuG5F09gsy_VmZ6Iz76x0yIfR5ZjYRFaZk8kIlUQQei8u9kk0bB_qFoaQQm";
            var parameters = new System.Collections.Specialized.NameValueCollection
            {
                { "content", GetLobbyData(lobbyList) }
            };
            using (WebClient wc = new WebClient())
            {
                wc.UploadValues(uri, parameters);
            }
        }

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
            return "{" + lobbies.TrimEnd(',') + "}";
        }

        private string AddField(string key, int value)
        {
            return $"\"{key}\":{value},";
        }
    }
}
