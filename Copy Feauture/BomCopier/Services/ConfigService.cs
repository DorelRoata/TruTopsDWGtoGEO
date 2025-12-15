using System.Text.Json;
using BomCopier.Models;

namespace BomCopier.Services
{
    public class ConfigService
    {
        private const string CONFIG_FILE = "config.json";
        private static readonly JsonSerializerOptions JsonOptions = new()
        {
            WriteIndented = true
        };

        public AppConfig Load()
        {
            try
            {
                if (File.Exists(CONFIG_FILE))
                {
                    string json = File.ReadAllText(CONFIG_FILE);
                    return JsonSerializer.Deserialize<AppConfig>(json) ?? new AppConfig();
                }
            }
            catch (Exception ex)
            {
                LogService.Log($"Error loading config: {ex.Message}");
            }

            return new AppConfig();
        }

        public void Save(AppConfig config)
        {
            try
            {
                string json = JsonSerializer.Serialize(config, JsonOptions);
                File.WriteAllText(CONFIG_FILE, json);
            }
            catch (Exception ex)
            {
                LogService.Log($"Error saving config: {ex.Message}");
                throw;
            }
        }

        public bool ConfigExists()
        {
            return File.Exists(CONFIG_FILE);
        }
    }
}
