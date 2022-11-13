using Modding;
using Networking;
using System.Net;
using System.Threading;
using UnityEngine;

namespace LobbyPoller
{
    public class LobbyPoller : IModEntryPoint
    {
        private static MultiplayerFilters _filters = default;
        private static string _discordHook =
            "https://discordapp.com/api/webhooks/1041396457648955453/5vWd1O07W2YKPEbdTK6o-_TFoibYRUsYle2imBM4Mg4xY_NTtmEHi7jbRyduqp4r7bOR";

        public void PostLoad()
        {
            _filters.HideInProgress = false;
            _filters.HidePassword = false;
            StartThread();
        }

        public void PreLoad() { }

        private void StartThread()
        {
            Thread thread = new Thread(new ThreadStart(LobbyPoll));
            thread.Start();
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
                    return;
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
                lobbyData += AddField("h", lobby.HasPassword ? "1" : "0");
                lobbyData += AddField("i", lobby.InProgress ? "1" : "0");
                lobbies += lobbyData.TrimEnd(',') + "},";
            }
            string data = "";
            data += AddField("u", SteamManager.ThisUser.Id.Value.ToString());
            data += AddField("l", "[" + lobbies.TrimEnd(',') + "]").TrimEnd((','));
            return "{" + data + "}";
        }

        /**
         * Returns JSON encoded int field with a trailing comma, e.g.
         * "h":0,
         */
        private string AddField(string key, string value)
        {
            return $"\"{key}\":{value},";
        }
    }
}
