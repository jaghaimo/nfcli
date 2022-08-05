using Modding;
using Networking;
using UnityEngine;
using System.Threading;

namespace LobbyPooler
{
    public class LobbyPooler : IModEntryPoint
    {
        private MultiplayerFilters _filters = default;

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
                Thread.Sleep(1000);
                lobbyList.GetNewLobbies();
                Debug.Log($"Lobbies refreshed, found {lobbyList.AllLobbies.Count} lobbies");
                foreach (SteamLobby steamLobby in lobbyList.AllLobbies)
                {
                    Debug.Log($"{steamLobby.Name} - {steamLobby.CurrentPlayers} / {steamLobby.MaxPlayers}");
                }
                lobbyList.StopRefreshing();
                Thread.Sleep(59000);
            }
        }
    }
}
