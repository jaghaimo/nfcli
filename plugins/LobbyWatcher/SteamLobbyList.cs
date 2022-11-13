using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Steamworks;
using Steamworks.Data;

public class SteamLobbyList
{
    public enum RefreshStatus
    {
        Done,
        Refreshing,
        Failed
    }

    public RefreshStatus Status
    {
        get { return this._status; }
    }

    public IReadOnlyCollection<SteamLobby> AllLobbies
    {
        get { return this._lobbies; }
    }

    public void RefreshLobbies()
    {
        this.StopRefreshing();
        LobbyWatcher.Log("Fetching lobbies, might take few seconds");
        if (!SteamClient.IsValid)
        {
            LobbyWatcher.Log("Steam Client is invalid");
            this._status = RefreshStatus.Failed;
            return;
        }
        this._lobbies.Clear();
        this._status = RefreshStatus.Refreshing;
        this._cancelToken = new CancellationTokenSource();
        this._fetchTask = this.FetchLobbiesAsync(this._cancelToken.Token);
    }

    public void StopRefreshing()
    {
        if (this._fetchTask == null)
        {
            return;
        }
        if (this._cancelToken == null)
        {
            return;
        }
        LobbyWatcher.Log("Cancelling existing task, did we wait long enough?");
        this._cancelToken.Cancel();
        this._status = RefreshStatus.Done;
        this._fetchTask = null;
        this._cancelToken = null;
    }

    public List<SteamLobby>? GetNewLobbies()
    {
        bool flag = this._status != RefreshStatus.Refreshing || this._fetchTask == null;
        if (this._status != RefreshStatus.Refreshing)
        {
            LobbyWatcher.Log("Lobbies are not refreshing - did the task create correctly?");
            return null;
        }

        if (this._fetchTask == null)
        {
            LobbyWatcher.Log("No data fetching task - did you forget to call RefreshLobbies()?");
            return null;
        }
        List<SteamLobby>? output = null;
        bool flag2 = this._newLobbies.Count > 0;
        if (flag2)
        {
            output = new List<SteamLobby>();
            while (!this._newLobbies.IsEmpty)
            {
                SteamLobby lobby;
                bool flag3 = this._newLobbies.TryTake(out lobby);
                if (flag3)
                {
                    output.Add(lobby);
                }
            }
            this._lobbies.AddRange(output);
        }
        bool isCompleted = this._fetchTask.IsCompleted;
        if (isCompleted)
        {
            this._status = RefreshStatus.Done;
            this._fetchTask = null;
        }
        return output;
    }

    private async Task<int> FetchLobbiesAsync(CancellationToken cancel)
    {
        int totalCount = 0;
        for (int page = 0; page < 10; page++)
        {
            if (cancel.IsCancellationRequested)
            {
                LobbyWatcher.Log("Cancellation request found, ending task");
                return totalCount;
            }
            LobbyQuery query = SteamMatchmaking.LobbyList;
            query.WithSlotsAvailable(0);
            query.WithKeyValue("page", page.ToString());
            query.FilterDistanceWorldwide();
            Lobby[] lobbies = await query.RequestAsync();
            if (lobbies != null)
            {
                totalCount += lobbies.Length;
                foreach (Lobby lobby in lobbies)
                {
                    this._newLobbies.Add(new SteamLobby(lobby));
                }
            }
        }
        return totalCount;
    }

    private RefreshStatus _status = RefreshStatus.Done;

    private List<SteamLobby> _lobbies = new List<SteamLobby>();

    private Task<int>? _fetchTask;

    private CancellationTokenSource? _cancelToken = null;

    private ConcurrentBag<SteamLobby> _newLobbies = new ConcurrentBag<SteamLobby>();
}
