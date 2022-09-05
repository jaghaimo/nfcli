using Bundles;
using Modding;
using Ships;
using System;
using System.Collections.Generic;
using UnityEngine;

namespace HullDumper
{
    public class HullDumper : IModEntryPoint
    {
        public void PostLoad()
        {
            IReadOnlyCollection<Hull> allHulls = BundleManager.Instance.AllHulls;
            foreach (Hull hull in allHulls)
            {
                ulong sourceModId = hull.SourceModId ?? 0;
                string hullName = sanitizeHullName(hull.SaveKey.ToLower());
                string fileName = getFileName(sourceModId, hullName);
                Console.WriteLine($"Writing to {fileName} file...");
                HullSpec hullSpec = GetHull(hull);
                System.IO.File.WriteAllText(
                    $"{ModDatabase.LocalModDirectory}{fileName}",
                    hullSpec.ToString()
                );
            }
        }

        public void PreLoad() { }

        private string sanitizeHullName(string hullName)
        {
            hullName = hullName.Replace(' ', '_');
            foreach (char c in System.IO.Path.GetInvalidFileNameChars())
            {
                hullName = hullName.Replace(c, '_');
            }
            return hullName;
        }

        private string getFileName(ulong sourceModId, string hullName)
        {
            string fileName = $"{sourceModId}_{hullName}.json";
            if (System.IO.File.Exists(fileName))
            {
                return getFileName(sourceModId, hullName + "_1");
            }
            return fileName;
        }

        private HullSpec GetHull(Hull hull)
        {
            HullSpec hullSpec = new HullSpec(hull.SaveKey, hull.FullClassification);
            foreach (HullSocket socket in hull.GetAllSockets())
            {
                SocketSpec socketSpec = new SocketSpec
                {
                    Key = socket.Key,
                    Size = socket.Size.Dimensions
                };
                hullSpec.Add(socket.Type, socketSpec);
            }
            Console.WriteLine(hullSpec);
            return hullSpec;
        }
    }

    public class HullSpec
    {
        public HullSpec(string key, string name)
        {
            Key = key;
            Name = name;
            Surfaces = new List<SocketSpec>();
            Compartments = new List<SocketSpec>();
            Modules = new List<SocketSpec>();
        }

        public string Key { get; set; }
        public string Name { get; set; }
        public List<SocketSpec> Surfaces { get; set; }
        public List<SocketSpec> Compartments { get; set; }
        public List<SocketSpec> Modules { get; set; }

        public void Add(HullSocketType type, SocketSpec socket)
        {
            switch (type)
            {
                case HullSocketType.Surface:
                    Surfaces.Add(socket);
                    break;
                case HullSocketType.Compartment:
                    Compartments.Add(socket);
                    break;
                case HullSocketType.Module:
                    Modules.Add(socket);
                    break;
                default:
                    break;
            }
        }

        private string SocketsToString(List<SocketSpec> sockets)
        {
            return "    " + string.Join(",\n    ", sockets);
        }

        private string Sanitize(string Text)
        {
            return Text.Replace("\"", "\\\"");
        }

        public override string ToString()
        {
            return "{\n"
                + $"  \"key\": \"{Sanitize(Key)}\",\n"
                + $"  \"name\": \"{Sanitize(Name)}\",\n"
                + "  \"mounts\": {\n"
                + SocketsToString(Surfaces)
                + "\n  },\n"
                + "  \"compartments\": {\n"
                + SocketsToString(Compartments)
                + "\n  },\n"
                + "  \"modules\": {\n"
                + SocketsToString(Modules)
                + "\n  }\n"
                + "}\n";
        }
    }

    public class SocketSpec
    {
        public string Key { get; set; }
        public Vector3Int Size { get; set; }

        public override string ToString()
        {
            return $"\"{Key}\": \"{Size.x}x{Size.y}x{Size.z}\"";
        }
    }
}
