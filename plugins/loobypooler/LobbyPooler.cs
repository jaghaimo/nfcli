using Modding;
using Networking;
using System.Collections;
using System.Net;
using System.Threading;
using UnityEngine;
using UnityEngine.Networking;

namespace LobbyPooler
{
    public class LobbyPooler : IModEntryPoint
    {
        private static MultiplayerFilters _filters = default;
        private UnityWebRequest www = UnityWebRequest.Get("https://discord.com/api/webhooks/1005583148698046515/qHx3Lbkg8TuG5F09gsy_VmZ6Iz76x0yIfR5ZjYRFaZk8kIlUQQei8u9kk0bB_qFoaQQm");

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

        public void LobbyPool()
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
                SendData(lobbyList.AllLobbies.ToString());
                Thread.Sleep(60000);
            }
        }

        public void SendData(string lobbyData)
        {
            string URI = "https://discord.com/api/webhooks/1005583148698046515/qHx3Lbkg8TuG5F09gsy_VmZ6Iz76x0yIfR5ZjYRFaZk8kIlUQQei8u9kk0bB_qFoaQQm";
            var parameters = new System.Collections.Specialized.NameValueCollection();
            parameters.Add("content", lobbyData);
            using (WebClient wc = new WebClient())
            {
                wc.UploadValues(URI, parameters);
            }
        }
    }
}
