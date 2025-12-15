using BomCopier.Models;
using BomCopier.Services;

namespace BomCopier.Forms
{
    public partial class MainForm : Form
    {
        private readonly ConfigService _configService;
        private readonly ExcelService _excelService;
        private readonly FileSearchService _fileSearchService;
        private readonly CopyService _copyService;

        private AppConfig _config;
        private List<BomRow> _allBomRows = new();
        private List<BomRow> _filteredRows = new();
        private List<BomRow> _queuedFiles = new();

        public MainForm()
        {
            InitializeComponent();

            _configService = new ConfigService();
            _excelService = new ExcelService();
            _fileSearchService = new FileSearchService();
            _copyService = new CopyService();

            _copyService.ProgressChanged += OnCopyProgressChanged;

            _config = _configService.Load();

            // Show settings on first run
            if (!_configService.ConfigExists())
            {
                ShowSettings();
            }

            LoadConfigToUI();
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
            if (settingsForm.ShowDialog() == DialogResult.OK)
            {
                _config = settingsForm.Config;
                // Reload BOM if one was loaded
                if (_allBomRows.Count > 0 && !string.IsNullOrEmpty(_config.LastBomFile))
                {
                    LoadBomFile(_config.LastBomFile);
                }
            }
        }

        private void LoadBomFile(string filePath)
        {
            try
            {
                lblStatus.Text = "Loading BOM...";
                Application.DoEvents();

                _allBomRows = _excelService.LoadBom(filePath, _config);
                _config.LastBomFile = filePath;
                _configService.Save(_config);

                // Populate materials dropdown
                var materials = _excelService.GetUniqueMaterials(_allBomRows);
                cmbMaterial.Items.Clear();
                cmbMaterial.Items.Add("(All)");
                foreach (var material in materials)
                {
                    cmbMaterial.Items.Add(material);
                }

                if (cmbMaterial.Items.Count > 0)
                {
                    cmbMaterial.SelectedIndex = 0;
                }

                lblStatus.Text = $"Loaded {_allBomRows.Count} items from BOM";
                lblFileCount.Text = $"{_allBomRows.Count} items";

                // Search for files if source directory is set
                if (!string.IsNullOrWhiteSpace(txtSourceDirectory.Text))
                {
                    SearchForFiles();
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

        private void SearchForFiles()
        {
            if (_allBomRows.Count == 0)
                return;

            lblStatus.Text = "Searching for files...";
            Application.DoEvents();

            // FindFiles returns expanded list with separate entries for normal and FLO versions
            _allBomRows = _fileSearchService.FindFiles(_allBomRows, txtSourceDirectory.Text);
            RefreshAvailableList();

            int found = _allBomRows.Count(r => r.IsFound);
            int total = _allBomRows.Count;
            lblStatus.Text = $"Found {found} of {total} file entries";
        }

        private void RefreshAvailableList()
        {
            string selectedMaterial = cmbMaterial.SelectedItem?.ToString() ?? "(All)";
            _filteredRows = _fileSearchService.FilterByMaterial(_allBomRows, selectedMaterial);

            // Apply search filter
            string search = txtSearchAvailable.Text.Trim().ToLower();
            var displayList = _filteredRows;
            if (!string.IsNullOrEmpty(search))
            {
                displayList = displayList.Where(r =>
                    r.TargetFileName.ToLower().Contains(search) ||
                    r.Material.ToLower().Contains(search)).ToList();
            }

            // Exclude already queued items
            displayList = displayList.Where(r => !_queuedFiles.Contains(r)).ToList();

            lstAvailable.BeginUpdate();
            lstAvailable.Items.Clear();
            foreach (var row in displayList)
            {
                var item = new ListViewItem(row.TargetFileName);
                item.SubItems.Add(row.Quantity.ToString());
                item.SubItems.Add(row.IsFound ? "Yes" : "No");
                item.Tag = row;
                item.ForeColor = row.IsFound ? Color.FromArgb(223, 230, 233) : Color.FromArgb(99, 110, 114);
                lstAvailable.Items.Add(item);
            }
            lstAvailable.EndUpdate();

            lblFileCount.Text = $"{displayList.Count} available, {_queuedFiles.Count} queued";
        }

        private void RefreshQueueList()
        {
            string search = txtSearchQueue.Text.Trim().ToLower();
            var displayList = _queuedFiles;
            if (!string.IsNullOrEmpty(search))
            {
                displayList = displayList.Where(r =>
                    r.TargetFileName.ToLower().Contains(search)).ToList();
            }

            lstQueue.BeginUpdate();
            lstQueue.Items.Clear();
            foreach (var row in displayList)
            {
                var item = new ListViewItem(row.TargetFileName);
                item.SubItems.Add(row.Quantity.ToString());
                item.SubItems.Add(row.IsFound ? "Yes" : "No");
                item.Tag = row;
                item.ForeColor = row.IsFound ? Color.FromArgb(223, 230, 233) : Color.FromArgb(99, 110, 114);
                lstQueue.Items.Add(item);
            }
            lstQueue.EndUpdate();

            lblFileCount.Text = $"{lstAvailable.Items.Count} available, {_queuedFiles.Count} queued";
            btnStartCopy.Enabled = _queuedFiles.Count > 0;
        }

        private void AddSelectedToQueue()
        {
            foreach (ListViewItem item in lstAvailable.SelectedItems)
            {
                if (item.Tag is BomRow row && !_queuedFiles.Contains(row))
                {
                    _queuedFiles.Add(row);
                }
            }
            RefreshAvailableList();
            RefreshQueueList();
        }

        private void AddAllToQueue()
        {
            foreach (ListViewItem item in lstAvailable.Items)
            {
                if (item.Tag is BomRow row && !_queuedFiles.Contains(row))
                {
                    _queuedFiles.Add(row);
                }
            }
            RefreshAvailableList();
            RefreshQueueList();
        }

        private void RemoveSelectedFromQueue()
        {
            var toRemove = new List<BomRow>();
            foreach (ListViewItem item in lstQueue.SelectedItems)
            {
                if (item.Tag is BomRow row)
                {
                    toRemove.Add(row);
                }
            }
            foreach (var row in toRemove)
            {
                _queuedFiles.Remove(row);
            }
            RefreshAvailableList();
            RefreshQueueList();
        }

        private void ClearQueue()
        {
            _queuedFiles.Clear();
            RefreshAvailableList();
            RefreshQueueList();
        }

        private async void StartCopy()
        {
            if (_queuedFiles.Count == 0)
            {
                MessageBox.Show("No files in queue.", "Info", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            if (string.IsNullOrWhiteSpace(txtTargetDirectory.Text))
            {
                MessageBox.Show("Please select a target directory.", "Error", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            // Only copy files that were found
            var filesToCopy = _queuedFiles.Where(r => r.IsFound).ToList();
            int notFound = _queuedFiles.Count - filesToCopy.Count;

            if (filesToCopy.Count == 0)
            {
                MessageBox.Show("None of the queued files were found in the source directory.", "Error", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            string message = $"Copy {filesToCopy.Count} file(s) to:\n{txtTargetDirectory.Text}";
            if (notFound > 0)
            {
                message += $"\n\n({notFound} files will be skipped - not found)";
            }

            if (MessageBox.Show(message, "Confirm Copy", MessageBoxButtons.YesNo, MessageBoxIcon.Question) != DialogResult.Yes)
            {
                return;
            }

            // Disable UI during copy
            SetUIEnabled(false);
            progressBar.Value = 0;
            progressBar.Maximum = filesToCopy.Count;

            try
            {
                SaveDirectoriesToConfig();

                var result = await Task.Run(() =>
                    _copyService.CopyFiles(filesToCopy, txtTargetDirectory.Text, _config.OverwriteExisting));

                // Show summary
                string summary = $"Copy Complete!\n\n" +
                    $"Copied: {result.Copied}\n" +
                    $"Skipped: {result.Skipped}\n" +
                    $"Errors: {result.Errors}";

                if (result.Errors > 0 && result.ErrorMessages.Count > 0)
                {
                    summary += "\n\nErrors:\n" + string.Join("\n", result.ErrorMessages.Take(5));
                    if (result.ErrorMessages.Count > 5)
                    {
                        summary += $"\n... and {result.ErrorMessages.Count - 5} more (see log.txt)";
                    }
                }

                MessageBox.Show(summary, "Copy Complete", MessageBoxButtons.OK,
                    result.Errors > 0 ? MessageBoxIcon.Warning : MessageBoxIcon.Information);

                // Clear queue on success
                if (result.Errors == 0)
                {
                    ClearQueue();
                }

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

            progressBar.Maximum = total;
            progressBar.Value = current;
            lblStatus.Text = $"Copying {current}/{total}: {fileName}";
        }

        private void SetUIEnabled(bool enabled)
        {
            btnLoadBom.Enabled = enabled;
            btnSettings.Enabled = enabled;
            btnBrowseSource.Enabled = enabled;
            btnBrowseTarget.Enabled = enabled;
            btnAdd.Enabled = enabled;
            btnAddAll.Enabled = enabled;
            btnRemove.Enabled = enabled;
            btnClearQueue.Enabled = enabled;
            btnStartCopy.Enabled = enabled && _queuedFiles.Count > 0;
            cmbMaterial.Enabled = enabled;
            lstAvailable.Enabled = enabled;
            lstQueue.Enabled = enabled;
        }

        // Event Handlers

        private void btnLoadBom_Click(object sender, EventArgs e)
        {
            using var dialog = new OpenFileDialog
            {
                Filter = "Excel Files|*.xlsx;*.xls|All Files|*.*",
                Title = "Select BOM File"
            };

            if (!string.IsNullOrEmpty(_config.LastBomFile))
            {
                dialog.InitialDirectory = Path.GetDirectoryName(_config.LastBomFile);
            }

            if (dialog.ShowDialog() == DialogResult.OK)
            {
                LoadBomFile(dialog.FileName);
            }
        }

        private void btnSettings_Click(object sender, EventArgs e)
        {
            ShowSettings();
        }

        private void btnBrowseSource_Click(object sender, EventArgs e)
        {
            using var dialog = new FolderBrowserDialog
            {
                Description = "Select Source Directory",
                ShowNewFolderButton = false
            };

            if (!string.IsNullOrEmpty(txtSourceDirectory.Text) && Directory.Exists(txtSourceDirectory.Text))
            {
                dialog.SelectedPath = txtSourceDirectory.Text;
            }

            if (dialog.ShowDialog() == DialogResult.OK)
            {
                txtSourceDirectory.Text = dialog.SelectedPath;
                SaveDirectoriesToConfig();
                SearchForFiles();
            }
        }

        private void btnBrowseTarget_Click(object sender, EventArgs e)
        {
            using var dialog = new FolderBrowserDialog
            {
                Description = "Select Target Directory",
                ShowNewFolderButton = true
            };

            if (!string.IsNullOrEmpty(txtTargetDirectory.Text) && Directory.Exists(txtTargetDirectory.Text))
            {
                dialog.SelectedPath = txtTargetDirectory.Text;
            }

            if (dialog.ShowDialog() == DialogResult.OK)
            {
                txtTargetDirectory.Text = dialog.SelectedPath;
                SaveDirectoriesToConfig();
            }
        }

        private void cmbMaterial_SelectedIndexChanged(object sender, EventArgs e)
        {
            RefreshAvailableList();
        }

        private void txtSearchAvailable_TextChanged(object sender, EventArgs e)
        {
            RefreshAvailableList();
        }

        private void txtSearchQueue_TextChanged(object sender, EventArgs e)
        {
            RefreshQueueList();
        }

        private void btnAdd_Click(object sender, EventArgs e)
        {
            AddSelectedToQueue();
        }

        private void btnAddAll_Click(object sender, EventArgs e)
        {
            AddAllToQueue();
        }

        private void btnRemove_Click(object sender, EventArgs e)
        {
            RemoveSelectedFromQueue();
        }

        private void btnClearQueue_Click(object sender, EventArgs e)
        {
            ClearQueue();
        }

        private void btnStartCopy_Click(object sender, EventArgs e)
        {
            StartCopy();
        }

        private void lstAvailable_Click(object sender, EventArgs e)
        {
            AddSelectedToQueue();
        }

        private void lstQueue_Click(object sender, EventArgs e)
        {
            RemoveSelectedFromQueue();
        }

        private void lstAvailable_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter)
            {
                AddSelectedToQueue();
                e.Handled = true;
            }
        }

        private void lstQueue_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Delete)
            {
                RemoveSelectedFromQueue();
                e.Handled = true;
            }
        }

        // Drag and drop support
        private void MainForm_DragEnter(object sender, DragEventArgs e)
        {
            if (e.Data?.GetDataPresent(DataFormats.FileDrop) == true)
            {
                var files = (string[]?)e.Data.GetData(DataFormats.FileDrop);
                if (files?.Any(f => f.EndsWith(".xlsx", StringComparison.OrdinalIgnoreCase) ||
                                    f.EndsWith(".xls", StringComparison.OrdinalIgnoreCase)) == true)
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
            var excelFile = files?.FirstOrDefault(f =>
                f.EndsWith(".xlsx", StringComparison.OrdinalIgnoreCase) ||
                f.EndsWith(".xls", StringComparison.OrdinalIgnoreCase));

            if (excelFile != null)
            {
                LoadBomFile(excelFile);
            }
        }
    }
}
