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

    public string OwnerName { get; private set; }

    public SteamId LobbyOwnerID { get; private set; }

    public string Name { get; private set; }

    public GameMode Mode { get; private set; }

    public string SubMode { get; private set; }

    public string Map { get; private set; }

    public bool HasPassword { get; private set; }

    public bool InProgress { get; private set; }

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

    private Lobby _lobby;

    public List<Friend> Members;
}
