using BomCopier.Models;
using BomCopier.Services;

namespace BomCopier.Forms
{
    public partial class MainForm : Form
    {
        private const string PreferSuffixMode = "Prefer FLO";
        private const string NormalOnlyMode = "Normal only";
        private const string SuffixOnlyMode = "FLO only";
        private const string ShowBothMode = "Show both";

        private readonly ConfigService _configService;
        private readonly ExcelService _excelService;
        private readonly FileSearchService _fileSearchService;
        private readonly CopyService _copyService;

        private AppConfig _config;
        private List<BomRow> _bomRows = new();
        private List<BomRow> _resolvedRows = new();
        private readonly List<BomRow> _queuedFiles = new();
        private bool _bomLoaded;
        private bool _isBusy;

        public MainForm()
        {
            InitializeComponent();

            string iconPath = Path.Combine(AppContext.BaseDirectory, "bc_icon.ico");
            if (File.Exists(iconPath))
            {
                Icon = new Icon(iconPath);
            }

            _configService = new ConfigService();
            _excelService = new ExcelService();
            _fileSearchService = new FileSearchService();
            _copyService = new CopyService();
            _copyService.ProgressChanged += OnCopyProgressChanged;

            _config = _configService.Load();

            cmbVariant.Items.AddRange(new object[]
            {
                PreferSuffixMode,
                NormalOnlyMode,
                SuffixOnlyMode,
                ShowBothMode
            });
            cmbVariant.SelectedIndex = 0;

            if (!_configService.ConfigExists())
            {
                ShowSettings();
            }

            LoadConfigToUI();
            SetMaterials(Array.Empty<string>());
            UpdateActionState();
        }

        private void LoadConfigToUI()
        {
            txtSourceDirectory.Text = _config.SourceDirectory;
            txtTargetDirectory.Text = _config.TargetDirectory;
        }

        private void SaveDirectoriesToConfig()
        {
            _config.SourceDirectory = txtSourceDirectory.Text.Trim();
            _config.TargetDirectory = txtTargetDirectory.Text.Trim();
            _configService.Save(_config);
        }

        private void ShowSettings()
        {
            using var settingsForm = new SettingsForm(_config);
            if (settingsForm.ShowDialog() != DialogResult.OK)
            {
                return;
            }

            _config = settingsForm.Config;
            LoadConfigToUI();

            if (_bomLoaded && !string.IsNullOrEmpty(_config.LastBomFile))
            {
                LoadBomFile(_config.LastBomFile);
            }
        }

        private void LoadBomFile(string filePath)
        {
            try
            {
                lblStatus.Text = "Loading BOM...";
                Application.DoEvents();

                _bomRows = _excelService.LoadBom(filePath, _config);
                _resolvedRows.Clear();
                _queuedFiles.Clear();
                _bomLoaded = true;
                _config.LastBomFile = filePath;
                _configService.Save(_config);

                SetMaterials(_excelService.GetUniqueMaterials(_bomRows));
                lblStatus.Text = $"Loaded {_bomRows.Count} unique BOM part(s)";

                if (Directory.Exists(txtSourceDirectory.Text.Trim()))
                {
                    SearchForFiles();
                }
                else
                {
                    RefreshLists();
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Error loading BOM: {ex.Message}",
                    "Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
                lblStatus.Text = "Error loading BOM";
            }
        }

        private void SetMaterials(IEnumerable<string> materials)
        {
            cmbMaterial.BeginUpdate();
            cmbMaterial.Items.Clear();
            cmbMaterial.Items.Add("(All)");
            foreach (string material in materials)
            {
                cmbMaterial.Items.Add(material);
            }

            cmbMaterial.SelectedIndex = 0;
            cmbMaterial.EndUpdate();
            cmbMaterial.Enabled = !_isBusy && cmbMaterial.Items.Count > 1;
        }

        private void SearchForFiles()
        {
            string sourceDirectory = txtSourceDirectory.Text.Trim();
            if (!Directory.Exists(sourceDirectory))
            {
                lblStatus.Text = "Source folder is invalid";
                return;
            }

            lblStatus.Text = "Scanning source folder...";
            Application.DoEvents();

            var queuedKeys = _queuedFiles
                .Select(GetQueueKey)
                .ToHashSet(StringComparer.OrdinalIgnoreCase);

            if (_bomLoaded)
            {
                if (_bomRows.Count == 0)
                {
                    lblStatus.Text = "No BOM items loaded";
                    return;
                }

                _resolvedRows = _fileSearchService.FindFiles(
                    _bomRows,
                    sourceDirectory,
                    _config.TargetFileExtension);
            }
            else
            {
                _resolvedRows = _fileSearchService.LoadFilesFromDirectory(
                    sourceDirectory,
                    _config.TargetFileExtension);
                SetMaterials(Array.Empty<string>());
            }

            RemapQueue(queuedKeys);
            RefreshLists();

            int ready = _resolvedRows.Count(row => row.CanCopy);
            int ambiguous = _resolvedRows.Count(row => row.IsAmbiguous);
            lblStatus.Text = ambiguous > 0
                ? $"Scan complete: {ready} ready, {ambiguous} duplicate-name match(es) need attention"
                : $"Scan complete: {ready} drawing candidate(s) ready";
        }

        private void RemapQueue(HashSet<string> queuedKeys)
        {
            _queuedFiles.Clear();
            foreach (BomRow row in _resolvedRows.Where(row => row.CanCopy))
            {
                if (queuedKeys.Contains(GetQueueKey(row)) &&
                    !_queuedFiles.Any(queued => QueueKeysEqual(queued, row)))
                {
                    _queuedFiles.Add(row);
                }
            }
        }

        private void RefreshLists()
        {
            RefreshAvailableList();
            RefreshQueueList();
        }

        private void RefreshAvailableList()
        {
            string selectedMaterial = cmbMaterial.SelectedItem?.ToString() ?? "(All)";
            var materialRows = _fileSearchService.FilterByMaterial(_resolvedRows, selectedMaterial);
            var displayRows = ApplyVariantFilter(materialRows);

            string search = txtSearchAvailable.Text.Trim();
            if (!string.IsNullOrEmpty(search))
            {
                displayRows = displayRows.Where(row =>
                    row.TargetFileName.Contains(search, StringComparison.OrdinalIgnoreCase) ||
                    row.Material.Contains(search, StringComparison.OrdinalIgnoreCase)).ToList();
            }

            displayRows = displayRows
                .Where(row => !_queuedFiles.Any(queued => QueueKeysEqual(queued, row)))
                .ToList();

            int topIndex = lstAvailable.TopItem?.Index ?? 0;
            lstAvailable.BeginUpdate();
            lstAvailable.Items.Clear();
            foreach (BomRow row in displayRows)
            {
                lstAvailable.Items.Add(CreateListItem(row));
            }
            lstAvailable.EndUpdate();
            RestoreTopItem(lstAvailable, topIndex);

            UpdateActionState();
        }

        private void RefreshQueueList()
        {
            string search = txtSearchQueue.Text.Trim();
            var displayRows = string.IsNullOrEmpty(search)
                ? _queuedFiles.ToList()
                : _queuedFiles.Where(row =>
                    row.TargetFileName.Contains(search, StringComparison.OrdinalIgnoreCase) ||
                    row.Material.Contains(search, StringComparison.OrdinalIgnoreCase)).ToList();

            int topIndex = lstQueue.TopItem?.Index ?? 0;
            lstQueue.BeginUpdate();
            lstQueue.Items.Clear();
            foreach (BomRow row in displayRows)
            {
                lstQueue.Items.Add(CreateListItem(row));
            }
            lstQueue.EndUpdate();
            RestoreTopItem(lstQueue, topIndex);

            UpdateActionState();
        }

        private List<BomRow> ApplyVariantFilter(List<BomRow> rows)
        {
            if (!_bomLoaded)
            {
                return rows;
            }

            string mode = cmbVariant.SelectedItem?.ToString() ?? PreferSuffixMode;
            if (mode == NormalOnlyMode)
            {
                return rows.Where(row => !row.IsSuffixVersion).ToList();
            }

            if (mode == SuffixOnlyMode)
            {
                return rows.Where(row => row.IsSuffixVersion).ToList();
            }

            if (mode == ShowBothMode)
            {
                return rows;
            }

            return rows
                .GroupBy(GetPartKey, StringComparer.OrdinalIgnoreCase)
                .Select(group =>
                    group.FirstOrDefault(row => row.IsSuffixVersion && row.CanCopy) ??
                    group.FirstOrDefault(row => !row.IsSuffixVersion && row.CanCopy) ??
                    group.FirstOrDefault(row => row.IsSuffixVersion && row.IsAmbiguous) ??
                    group.FirstOrDefault(row => !row.IsSuffixVersion && row.IsAmbiguous) ??
                    group.First())
                .ToList();
        }

        private ListViewItem CreateListItem(BomRow row)
        {
            var item = new ListViewItem(row.TargetFileName);
            item.SubItems.Add(row.Quantity.ToString());
            item.SubItems.Add(row.IsSuffixVersion ? _config.FilenameSuffix : "Normal");
            item.SubItems.Add(GetStatusText(row));
            item.Tag = row;
            item.ForeColor = row.CanCopy
                ? Color.FromArgb(223, 230, 233)
                : row.IsAmbiguous
                    ? Color.FromArgb(235, 176, 95)
                    : Color.FromArgb(110, 120, 130);
            return item;
        }

        private static string GetStatusText(BomRow row)
        {
            if (row.IsAmbiguous)
            {
                return $"Duplicate ({row.MatchCount})";
            }

            return row.IsFound ? "Ready" : "Missing";
        }

        private void AddSelectedToQueue()
        {
            AddItemsToQueue(lstAvailable.SelectedItems.Cast<ListViewItem>());
        }

        private void AddAllToQueue()
        {
            AddItemsToQueue(lstAvailable.Items.Cast<ListViewItem>());
        }

        private void AddItemsToQueue(IEnumerable<ListViewItem> items)
        {
            int added = 0;
            int unavailable = 0;

            foreach (BomRow row in items.Select(item => item.Tag).OfType<BomRow>().ToList())
            {
                if (!row.CanCopy)
                {
                    unavailable++;
                    continue;
                }

                if (_queuedFiles.Any(queued => QueueKeysEqual(queued, row)))
                {
                    continue;
                }

                _queuedFiles.Add(row);
                added++;
            }

            RefreshLists();
            if (unavailable > 0)
            {
                lblStatus.Text = $"Added {added}; skipped {unavailable} missing or duplicate-name item(s)";
            }
            else if (added > 0)
            {
                lblStatus.Text = $"Added {added} drawing(s) to the copy queue";
            }
        }

        private void RemoveSelectedFromQueue()
        {
            var toRemove = lstQueue.SelectedItems
                .Cast<ListViewItem>()
                .Select(item => item.Tag)
                .OfType<BomRow>()
                .ToList();

            foreach (BomRow row in toRemove)
            {
                _queuedFiles.Remove(row);
            }

            RefreshLists();
            if (toRemove.Count > 0)
            {
                lblStatus.Text = $"Removed {toRemove.Count} drawing(s) from the queue";
            }
        }

        private void ClearQueue()
        {
            _queuedFiles.Clear();
            RefreshLists();
            lblStatus.Text = "Copy queue cleared";
        }

        private async void StartCopy()
        {
            if (_queuedFiles.Count == 0)
            {
                MessageBox.Show("No files in the copy queue.", "BOM Copier", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            string targetDirectory = txtTargetDirectory.Text.Trim();
            if (string.IsNullOrWhiteSpace(targetDirectory))
            {
                MessageBox.Show("Select a copy folder first.", "Copy Folder Required", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            var filesToCopy = _queuedFiles.Where(row => row.CanCopy).ToList();
            string message = $"Copy {filesToCopy.Count} drawing(s) to:\n\n{targetDirectory}";
            if (MessageBox.Show(message, "Confirm Copy", MessageBoxButtons.YesNo, MessageBoxIcon.Question) != DialogResult.Yes)
            {
                return;
            }

            SetUIEnabled(false);
            progressBar.Value = 0;
            progressBar.Maximum = Math.Max(1, filesToCopy.Count);

            try
            {
                SaveDirectoriesToConfig();
                CopyResult result = await Task.Run(() =>
                    _copyService.CopyFiles(filesToCopy, targetDirectory, _config.OverwriteExisting));

                foreach (BomRow copiedFile in result.CopiedFiles)
                {
                    _queuedFiles.Remove(copiedFile);
                }

                RefreshLists();

                string summary = $"Copy complete.\n\n" +
                    $"Copied: {result.Copied}\n" +
                    $"Skipped: {result.Skipped}\n" +
                    $"Errors: {result.Errors}\n" +
                    $"Remaining in queue: {_queuedFiles.Count}";

                if (result.ErrorMessages.Count > 0)
                {
                    summary += "\n\n" + string.Join("\n", result.ErrorMessages.Take(5));
                    if (result.ErrorMessages.Count > 5)
                    {
                        summary += $"\n...and {result.ErrorMessages.Count - 5} more (see log.txt)";
                    }
                }

                MessageBox.Show(
                    summary,
                    "Copy Complete",
                    MessageBoxButtons.OK,
                    result.Errors > 0 ? MessageBoxIcon.Warning : MessageBoxIcon.Information);

                lblStatus.Text = $"Copy complete: {result.Copied} copied, {result.Skipped} skipped, {result.Errors} errors";
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Copy failed: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                lblStatus.Text = "Copy failed";
            }
            finally
            {
                SetUIEnabled(true);
                progressBar.Value = 0;
            }
        }

        private void OnCopyProgressChanged(int current, int total, string fileName)
        {
            if (InvokeRequired)
            {
                Invoke(() => OnCopyProgressChanged(current, total, fileName));
                return;
            }

            progressBar.Maximum = Math.Max(1, total);
            progressBar.Value = Math.Min(current, progressBar.Maximum);
            lblStatus.Text = $"Copying {current}/{total}: {fileName}";
        }

        private void SetUIEnabled(bool enabled)
        {
            _isBusy = !enabled;
            btnLoadBom.Enabled = enabled;
            btnSettings.Enabled = enabled;
            btnBrowseSource.Enabled = enabled;
            btnScanSource.Enabled = enabled;
            btnBrowseTarget.Enabled = enabled;
            txtSourceDirectory.Enabled = enabled;
            txtTargetDirectory.Enabled = enabled;
            cmbMaterial.Enabled = enabled && cmbMaterial.Items.Count > 1;
            cmbVariant.Enabled = enabled && _bomLoaded;
            txtSearchAvailable.Enabled = enabled;
            txtSearchQueue.Enabled = enabled;
            lstAvailable.Enabled = enabled;
            lstQueue.Enabled = enabled;
            UpdateActionState();
        }

        private void UpdateActionState()
        {
            int availableCount = lstAvailable.Items.Count;
            lblFileCount.Text = $"{availableCount} available | {_queuedFiles.Count} queued";
            lblQueue.Text = $"Copy Queue ({_queuedFiles.Count})";

            btnAdd.Enabled = !_isBusy && lstAvailable.SelectedItems.Cast<ListViewItem>()
                .Any(item => item.Tag is BomRow row && row.CanCopy);
            btnAddAll.Enabled = !_isBusy && lstAvailable.Items.Cast<ListViewItem>()
                .Any(item => item.Tag is BomRow row && row.CanCopy);
            btnRemove.Enabled = !_isBusy && lstQueue.SelectedItems.Count > 0;
            btnClearQueue.Enabled = !_isBusy && _queuedFiles.Count > 0;
            btnStartCopy.Enabled = !_isBusy && _queuedFiles.Count > 0;
            btnStartCopy.Text = _queuedFiles.Count == 1
                ? "Copy 1 File"
                : $"Copy {_queuedFiles.Count} Files";
        }

        private static void RestoreTopItem(ListView listView, int previousTopIndex)
        {
            if (listView.Items.Count > 0 && previousTopIndex > 0)
            {
                listView.TopItem = listView.Items[Math.Min(previousTopIndex, listView.Items.Count - 1)];
            }
        }

        private static string GetPartKey(BomRow row) => row.NormalFileName + "\0" + row.Material;

        private static string GetQueueKey(BomRow row) => row.TargetFileName + "\0" + row.Material;

        private static bool QueueKeysEqual(BomRow left, BomRow right) =>
            GetQueueKey(left).Equals(GetQueueKey(right), StringComparison.OrdinalIgnoreCase);

        private static void SelectAllItems(ListView listView)
        {
            listView.BeginUpdate();
            foreach (ListViewItem item in listView.Items)
            {
                item.Selected = true;
            }
            listView.EndUpdate();
        }

        private void btnLoadBom_Click(object sender, EventArgs e)
        {
            using var dialog = new OpenFileDialog
            {
                Filter = "Excel Files|*.xlsx;*.xls|All Files|*.*",
                Title = "Select BOM File"
            };

            string? lastDirectory = Path.GetDirectoryName(_config.LastBomFile);
            if (!string.IsNullOrEmpty(lastDirectory) && Directory.Exists(lastDirectory))
            {
                dialog.InitialDirectory = lastDirectory;
            }

            if (dialog.ShowDialog() == DialogResult.OK)
            {
                LoadBomFile(dialog.FileName);
            }
        }

        private void btnSettings_Click(object sender, EventArgs e) => ShowSettings();

        private void btnBrowseSource_Click(object sender, EventArgs e)
        {
            using var dialog = new FolderBrowserDialog
            {
                Description = "Select the folder containing DWG files",
                ShowNewFolderButton = false,
                SelectedPath = Directory.Exists(txtSourceDirectory.Text) ? txtSourceDirectory.Text : string.Empty
            };

            if (dialog.ShowDialog() == DialogResult.OK)
            {
                txtSourceDirectory.Text = dialog.SelectedPath;
                SaveDirectoriesToConfig();
                SearchForFiles();
            }
        }

        private void btnScanSource_Click(object sender, EventArgs e)
        {
            SaveDirectoriesToConfig();
            SearchForFiles();
        }

        private void btnBrowseTarget_Click(object sender, EventArgs e)
        {
            using var dialog = new FolderBrowserDialog
            {
                Description = "Select the copy destination for this batch",
                ShowNewFolderButton = true,
                SelectedPath = Directory.Exists(txtTargetDirectory.Text) ? txtTargetDirectory.Text : string.Empty
            };

            if (dialog.ShowDialog() == DialogResult.OK)
            {
                txtTargetDirectory.Text = dialog.SelectedPath;
                SaveDirectoriesToConfig();
            }
        }

        private void cmbMaterial_SelectedIndexChanged(object sender, EventArgs e) => RefreshAvailableList();

        private void cmbVariant_SelectedIndexChanged(object sender, EventArgs e) => RefreshAvailableList();

        private void txtSearchAvailable_TextChanged(object sender, EventArgs e) => RefreshAvailableList();

        private void txtSearchQueue_TextChanged(object sender, EventArgs e) => RefreshQueueList();

        private void lstAvailable_SelectedIndexChanged(object sender, EventArgs e) => UpdateActionState();

        private void lstQueue_SelectedIndexChanged(object sender, EventArgs e) => UpdateActionState();

        private void btnAdd_Click(object sender, EventArgs e) => AddSelectedToQueue();

        private void btnAddAll_Click(object sender, EventArgs e) => AddAllToQueue();

        private void btnRemove_Click(object sender, EventArgs e) => RemoveSelectedFromQueue();

        private void btnClearQueue_Click(object sender, EventArgs e) => ClearQueue();

        private void btnStartCopy_Click(object sender, EventArgs e) => StartCopy();

        private void lstAvailable_DoubleClick(object sender, EventArgs e) => AddSelectedToQueue();

        private void lstQueue_DoubleClick(object sender, EventArgs e) => RemoveSelectedFromQueue();

        private void lstAvailable_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.Control && e.KeyCode == Keys.A)
            {
                SelectAllItems(lstAvailable);
                e.SuppressKeyPress = true;
            }
            else if (e.KeyCode == Keys.Enter)
            {
                AddSelectedToQueue();
                e.SuppressKeyPress = true;
            }
        }

        private void lstQueue_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.Control && e.KeyCode == Keys.A)
            {
                SelectAllItems(lstQueue);
                e.SuppressKeyPress = true;
            }
            else if (e.KeyCode == Keys.Delete)
            {
                RemoveSelectedFromQueue();
                e.SuppressKeyPress = true;
            }
        }

        private void MainForm_DragEnter(object sender, DragEventArgs e)
        {
            if (e.Data?.GetDataPresent(DataFormats.FileDrop) == true)
            {
                var files = (string[]?)e.Data.GetData(DataFormats.FileDrop);
                if (files?.Any(file =>
                    file.EndsWith(".xlsx", StringComparison.OrdinalIgnoreCase) ||
                    file.EndsWith(".xls", StringComparison.OrdinalIgnoreCase)) == true)
                {
                    e.Effect = DragDropEffects.Copy;
                    return;
                }
            }

            e.Effect = DragDropEffects.None;
        }

        private void MainForm_DragDrop(object sender, DragEventArgs e)
        {
            var files = (string[]?)e.Data?.GetData(DataFormats.FileDrop);
            string? excelFile = files?.FirstOrDefault(file =>
                file.EndsWith(".xlsx", StringComparison.OrdinalIgnoreCase) ||
                file.EndsWith(".xls", StringComparison.OrdinalIgnoreCase));

            if (excelFile != null)
            {
                LoadBomFile(excelFile);
            }
        }
    }
}
