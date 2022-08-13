using System.Collections.Generic;
using System.Linq;
using Steamworks;
using Steamworks.Data;

public class SteamLobby
{

    public enum GameMode
    {
        Unknown,
        Skirmish
    }

    public SteamId LobbyID
    {
        get
        {
            return this._lobby.Id;
        }
    }

    public SteamId ConnectionOwnerID
    {
        get
        {
            return this._lobby.Owner.Id;
        }
    }

    public string OwnerName { get; private set; }

    public SteamId LobbyOwnerID { get; private set; }

    public string Name { get; private set; }

    public GameMode Mode { get; private set; }

    public string SubMode { get; private set; }

    public string Map { get; private set; }

    public bool HasPassword { get; private set; }

    public bool InProgress { get; private set; }

    public int CurrentPlayers
    {
        get
        {
            return this._lobby.MemberCount;
        }
    }

    public int MaxPlayers
    {
        get
        {
            return this._lobby.MaxMembers;
        }
    }

    public bool HasFullInfo { get; private set; } = false;

    public SteamLobby(Lobby lobby)
    {
        this._lobby = lobby;
        this.Name = this._lobby.GetData("name");
        this.OwnerName = this._lobby.GetData("ownerName");
        ulong id;
        bool flag = ulong.TryParse(this._lobby.GetData("ownerId"), out id);
        if (flag)
        {
            this.LobbyOwnerID = new SteamId
            {
                Value = id
            };
        }
        int modeInt;
        bool flag2 = int.TryParse(this._lobby.GetData("gamemode"), out modeInt);
        if (flag2)
        {
            this.Mode = (GameMode)modeInt;
        }
        else
        {
            this.Mode = GameMode.Unknown;
        }
        this.SubMode = this._lobby.GetData("submode");
        this.Map = this._lobby.GetData("map");
        this.HasPassword = (this._lobby.GetData("password") == "1");
        this.InProgress = (this._lobby.GetData("inprogress") == "1");
        string hostNetLocationStr = this._lobby.GetData("netloc");
        this.Members = this._lobby.Members.ToList<Friend>();
    }

    public void LeaveLobby()
    {
        this._lobby.Leave();
    }

    public override string ToString()
    {
        return string.Format("Lobby \"{0}\" ({1}) owned by \"{2}\" ({3})", new object[]
        {
                this.Name,
                this.LobbyID,
                this.OwnerName,
                this.LobbyOwnerID
        });
    }

    public const string KeyName = "name";

    public const string KeyGameMode = "gamemode";

    public const string KeySubMode = "submode";

    public const string KeyHasPassword = "password";

    public const string KeyMapName = "map";

    public const string KeyInProgress = "inprogress";

    public const string KeyNetLocation = "netloc";

    public const string KeyOwnerName = "ownerName";

    public const string KeyOwnerId = "ownerId";

    public const string KeyPage = "page";

    public const int MaximumPages = 10;

    private Lobby _lobby;

    public List<Friend> Members;
}
