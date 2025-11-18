"""PySide6 desktop application for Phase 0 MVP."""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QListWidget,
    QSplitter,
    QLineEdit,
    QAbstractItemView,
    QSpinBox,
)

from .config import CONFIG
from .localization import translate
from .data_loader import DataLoader, DataFrameBundle
from .analysis import (
    compute_descriptive_statistics,
    one_sample_t_test,
    independent_t_test,
    create_histogram,
    create_scatter_plot,
)
from .planner import RuleBasedPlanner, AnalysisPlan
from .reporting import ReportBuilder


@dataclass
class AnalysisContext:
    data: Optional[DataFrameBundle] = None
    language: str = CONFIG.default_language
    last_results: Optional[Dict[str, Any]] = None
    last_chart_path: Optional[Path] = None


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(translate("app.title", CONFIG.default_language))
        self.resize(1200, 800)

        self.context = AnalysisContext()
        self.report_builder = ReportBuilder(language=self.context.language)

        self._create_menu()
        self._create_widgets()
        self._connect_signals()

    # region UI setup
    def _create_menu(self) -> None:
        menubar = self.menuBar()

        file_menu = menubar.addMenu(translate("menu.file", self.context.language))
        open_action = QAction(translate("action.open_file", self.context.language), self)
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)

        toggle_language_action = QAction(translate("action.toggle_language", self.context.language), self)
        toggle_language_action.triggered.connect(self._on_toggle_language)
        file_menu.addAction(toggle_language_action)

    def _create_widgets(self) -> None:
        container = QWidget(self)
        main_layout = QHBoxLayout(container)

        self.left_panel = self._build_left_panel()
        self.right_panel = self._build_right_panel()

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.left_panel)
        splitter.addWidget(self.right_panel)
        splitter.setSizes([400, 800])

        main_layout.addWidget(splitter)
        self.setCentralWidget(container)

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)

        self.label_step1 = QLabel(translate("wizard.step1", self.context.language))
        layout.addWidget(self.label_step1)

        self.button_open = QPushButton(translate("action.open_file", self.context.language))
        layout.addWidget(self.button_open)

        self.button_sample = QPushButton(translate("label.sample_data", self.context.language))
        layout.addWidget(self.button_sample)

        self.label_selected_file = QLabel(f"{translate('label.selected_file', self.context.language)}: -")
        layout.addWidget(self.label_selected_file)

        layout.addSpacing(12)
        self.label_step2 = QLabel(translate("wizard.step2", self.context.language))
        layout.addWidget(self.label_step2)

        self.analysis_combo = QComboBox()
        self.analysis_combo.addItem(translate("analysis.descriptive", self.context.language), "descriptive")
        self.analysis_combo.addItem(translate("analysis.t_test_one_sample", self.context.language), "t_test_one_sample")
        self.analysis_combo.addItem(translate("analysis.t_test_two_sample", self.context.language), "t_test_two_sample")
        layout.addWidget(self.analysis_combo)

        self.column_list = QListWidget()
        self.column_list.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.column_list)

        self.group_list = QListWidget()
        self.group_list.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.group_list)

        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("Population mean (default 0)")
        layout.addWidget(self.reference_input)

        layout.addSpacing(8)
        self.label_step2b = QLabel(translate("placeholder.instructions", self.context.language))
        self.instructions_input = QTextEdit()
        self.instructions_input.setPlaceholderText(translate("placeholder.instructions", self.context.language))
        layout.addWidget(self.label_step2b)
        layout.addWidget(self.instructions_input)

        self.button_plan = QPushButton(translate("action.ai_planner", self.context.language))
        layout.addWidget(self.button_plan)

        layout.addSpacing(8)
        # Chart settings section
        self.chart_settings_label = QLabel(translate("label.chart_settings", self.context.language))
        layout.addWidget(self.chart_settings_label)

        self.chart_title_input = QLineEdit()
        self.chart_title_input.setPlaceholderText(translate("label.chart_title", self.context.language))
        layout.addWidget(self.chart_title_input)

        self.palette_combo = QComboBox()
        self.palette_combo.addItems(["", "deep", "muted", "pastel", "bright", "dark", "colorblind"])
        self.palette_combo.setEditable(False)
        self.palette_combo.setPlaceholderText(translate("label.palette", self.context.language))
        layout.addWidget(self.palette_combo)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 32)
        self.font_size_spin.setValue(12)
        self.font_size_spin.setPrefix(translate("label.font_size", self.context.language) + ": ")
        layout.addWidget(self.font_size_spin)

        self.bins_spin = QSpinBox()
        self.bins_spin.setRange(5, 100)
        self.bins_spin.setValue(20)
        self.bins_spin.setPrefix(translate("label.bins", self.context.language) + ": ")
        layout.addWidget(self.bins_spin)

        self.point_size_spin = QSpinBox()
        self.point_size_spin.setRange(10, 200)
        self.point_size_spin.setValue(40)
        self.point_size_spin.setPrefix(translate("label.point_size", self.context.language) + ": ")
        layout.addWidget(self.point_size_spin)

        self.apply_chart_button = QPushButton(translate("action.apply_chart", self.context.language))
        layout.addWidget(self.apply_chart_button)

        layout.addSpacing(12)
        self.label_step3 = QLabel(translate("wizard.step3", self.context.language))
        layout.addWidget(self.label_step3)

        self.button_run = QPushButton(translate("action.run_analysis", self.context.language))
        layout.addWidget(self.button_run)

        self.button_export_pdf = QPushButton(translate("action.export_pdf", self.context.language))
        layout.addWidget(self.button_export_pdf)
        self.button_export_html = QPushButton(translate("action.export_html", self.context.language))
        layout.addWidget(self.button_export_html)

        layout.addStretch()
        return panel

    def _build_right_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)

        self.results_label = QLabel(translate("label.results", self.context.language))
        layout.addWidget(self.results_label)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

        self.explanation_label = QLabel(translate("label.explanation", self.context.language))
        layout.addWidget(self.explanation_label)

        self.explanation_text = QTextEdit()
        self.explanation_text.setReadOnly(True)
        layout.addWidget(self.explanation_text)

        self.code_label = QLabel(translate("label.code", self.context.language))
        layout.addWidget(self.code_label)

        self.code_text = QTextEdit()
        self.code_text.setReadOnly(True)
        self.code_text.setFontFamily("Fira Code")
        layout.addWidget(self.code_text)

        self.plot_label = QLabel(translate("label.plot", self.context.language))
        layout.addWidget(self.plot_label)

        self.plot_image = QLabel()
        self.plot_image.setAlignment(Qt.AlignCenter)
        self.plot_image.setMinimumSize(QSize(400, 300))
        layout.addWidget(self.plot_image)

        return panel

    def _connect_signals(self) -> None:
        self.button_open.clicked.connect(self._on_open_file)
        self.button_sample.clicked.connect(self._on_load_sample)
        self.button_run.clicked.connect(self._on_run_analysis)
        self.button_export_pdf.clicked.connect(lambda: self._export_report("pdf"))
        self.button_export_html.clicked.connect(lambda: self._export_report("html"))
        self.button_plan.clicked.connect(self._on_plan)
        self.apply_chart_button.clicked.connect(self._re_render_chart)
        self.analysis_combo.currentIndexChanged.connect(self._update_ui_state)

    # endregion

    # region event handlers
    def _on_open_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            translate("action.open_file", self.context.language),
            str(Path.home()),
            "CSV/Excel (*.csv *.xlsx *.xls)",
        )
        if file_path:
            self._load_data(Path(file_path))

    def _on_load_sample(self) -> None:
        try:
            bundle = DataLoader.load_sample()
            self._set_data_bundle(bundle)
            self.label_selected_file.setText(f"{translate('label.selected_file', self.context.language)}: sample_data.csv")
        except Exception as exc:
            self._show_error(str(exc))

    def _load_data(self, path: Path) -> None:
        try:
            bundle = DataLoader.load(path)
            self._set_data_bundle(bundle)
            self.label_selected_file.setText(f"{translate('label.selected_file', self.context.language)}: {path.name}")
        except Exception:
            self._show_error(translate("error.invalid_file", self.context.language))

    def _set_data_bundle(self, bundle: DataFrameBundle) -> None:
        self.context.data = bundle
        self.column_list.clear()
        self.group_list.clear()
        for col in bundle.numeric_columns:
            self.column_list.addItem(col)
        for col in bundle.categorical_columns:
            self.group_list.addItem(col)
        self.results_text.setText(translate("info.ready", self.context.language))

    def _on_run_analysis(self) -> None:
        if not self.context.data:
            self._show_error(translate("error.invalid_file", self.context.language))
            return
        analysis_tag = self.analysis_combo.currentData()
        try:
            results = self._execute_analysis(analysis_tag)
            self.context.last_results = results
            self._display_results(results)
            self.results_text.append("\n" + translate("info.completed", self.context.language))
        except Exception as exc:
            self._show_error(str(exc))

    def _on_plan(self) -> None:
        instruction = self.instructions_input.toPlainText().strip()
        if not instruction:
            return
        plan: AnalysisPlan = RuleBasedPlanner.plan(instruction)
        index = {
            "descriptive": 0,
            "t_test_one_sample": 1,
            "t_test_two_sample": 2,
        }.get(plan.analysis_type, 0)
        self.analysis_combo.setCurrentIndex(index)
        if plan.reference_value is not None:
            self.reference_input.setText(str(plan.reference_value))
        self.explanation_text.setText(f"Planner notes: {plan.notes}")

    def _on_toggle_language(self) -> None:
        new_lang = "en" if self.context.language == "zh" else "zh"
        self.context.language = new_lang
        self._refresh_labels()

    def _export_report(self, format_: str) -> None:
        if not self.context.last_results:
            self._show_error("No results to export")
            return

        context = self._report_context(self.context.last_results)
        filename = f"report_{self.analysis_combo.currentData()}.{format_}"
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            translate("action.export_pdf" if format_ == "pdf" else "action.export_html", self.context.language),
            str(CONFIG.paths.reports_dir / filename),
            "PDF Files (*.pdf)" if format_ == "pdf" else "HTML Files (*.html)",
        )
        if not save_path:
            return
        builder = ReportBuilder(language=self.context.language)
        if format_ == "pdf":
            builder.save_pdf(context, Path(save_path))
        else:
            builder.save_html(context, Path(save_path))
        QMessageBox.information(self, "Success", f"Report saved to {save_path}")

    # endregion

    # region helpers
    def _refresh_labels(self) -> None:
        lang = self.context.language
        self.setWindowTitle(translate("app.title", lang))
        self.label_step1.setText(translate("wizard.step1", lang))
        self.label_step2.setText(translate("wizard.step2", lang))
        self.label_step2b.setText(translate("placeholder.instructions", lang))
        self.label_step3.setText(translate("wizard.step3", lang))
        self.button_open.setText(translate("action.open_file", lang))
        self.button_sample.setText(translate("label.sample_data", lang))
        self.button_run.setText(translate("action.run_analysis", lang))
        self.button_export_pdf.setText(translate("action.export_pdf", lang))
        self.button_export_html.setText(translate("action.export_html", lang))
        self.button_plan.setText(translate("action.ai_planner", lang))
        self.chart_settings_label.setText(translate("label.chart_settings", lang))
        self.chart_title_input.setPlaceholderText(translate("label.chart_title", lang))
        self.apply_chart_button.setText(translate("action.apply_chart", lang))
        self.results_label.setText(translate("label.results", lang))
        self.explanation_label.setText(translate("label.explanation", lang))
        self.code_label.setText(translate("label.code", lang))
        self.plot_label.setText(translate("label.plot", lang))

        self.analysis_combo.blockSignals(True)
        self.analysis_combo.clear()
        self.analysis_combo.addItem(translate("analysis.descriptive", lang), "descriptive")
        self.analysis_combo.addItem(translate("analysis.t_test_one_sample", lang), "t_test_one_sample")
        self.analysis_combo.addItem(translate("analysis.t_test_two_sample", lang), "t_test_two_sample")
        self.analysis_combo.blockSignals(False)

    def _show_error(self, message: str) -> None:
        QMessageBox.critical(self, "Error", message)

    def _re_render_chart(self) -> None:
        """Re-render chart using current settings and last results."""
        if not self.context.data or not self.context.last_results:
            return
        # Trigger fresh chart based on last analysis
        analysis_tag = self.context.last_results.get("analysis")
        try:
            results = self._execute_analysis(analysis_tag)
            # Do not overwrite text results, only update chart
            self.context.last_results["chart_path"] = results.get("chart_path")
        except Exception as exc:
            self._show_error(str(exc))

    def _execute_analysis(self, analysis_tag: str) -> Dict[str, Any]:
        bundle = self.context.data
        assert bundle is not None
        column_item = self.column_list.currentItem()
        if not column_item and analysis_tag != "t_test_two_sample":
            raise ValueError(translate("error.no_numeric", self.context.language))

        column = column_item.text() if column_item else bundle.numeric_columns[0]
        code_lines = []
        result_data: Dict[str, Any] = {}
        explanation = ""
        chart_bytes: Optional[bytes] = None

        # Chart settings
        title = self.chart_title_input.text().strip() or None
        palette = self.palette_combo.currentText().strip() or None
        font_size = int(self.font_size_spin.value())
        bins = int(self.bins_spin.value())
        point_size = int(self.point_size_spin.value())

        if analysis_tag == "descriptive":
            stats = compute_descriptive_statistics(bundle.dataframe, column)
            result_data["statistics"] = stats
            explanation = self._build_explanation("descriptive", stats)
            chart_bytes = create_histogram(bundle.dataframe, column, title=title, bins=bins, palette=palette, font_size=font_size)
            code_lines = [
                "import pandas as pd",
                "import seaborn as sns",
                "import matplotlib.pyplot as plt",
                f"df = pd.read_csv('{bundle.path}')" if bundle.path else "# Data loaded from sample",
                f"stats = df['{column}'].describe()",
                "sns.histplot(df['{col}'], kde=True, bins={bins})".format(col=column, bins=bins),
                "plt.show()",
            ]
        elif analysis_tag == "t_test_one_sample":
            reference = float(self.reference_input.text() or 0.0)
            outcome = one_sample_t_test(bundle.dataframe, column, reference)
            result_data["statistics"] = outcome.to_dict()
            explanation = self._build_explanation("t_test_one_sample", outcome.to_dict())
            chart_bytes = create_histogram(bundle.dataframe, column, title=title, bins=bins, palette=palette, font_size=font_size)
            code_lines = [
                "from scipy import stats",
                f"t_stat, p_value = stats.ttest_1samp(df['{column}'], {reference})",
            ]
        elif analysis_tag == "t_test_two_sample":
            group_item = self.group_list.currentItem()
            if not group_item:
                raise ValueError("Please select a group column")
            group_column = group_item.text()
            outcome = independent_t_test(bundle.dataframe, column, group_column)
            result_data["statistics"] = outcome.to_dict()
            explanation = self._build_explanation("t_test_two_sample", outcome.to_dict())
            chart_bytes = create_histogram(bundle.dataframe, column, title=title, bins=bins, palette=palette, font_size=font_size)
            code_lines = [
                "from scipy import stats",
                f"grouped = df.groupby('{group_column}')['{column}']",
                "g1, g2 = [grp for _, grp in grouped]",
                "t_stat, p_value = stats.ttest_ind(g1, g2, equal_var=False)",
            ]
        else:
            raise NotImplementedError(analysis_tag)

        chart_path = None
        if chart_bytes:
            chart_path = CONFIG.paths.reports_dir / "latest_chart.png"
            chart_path.write_bytes(chart_bytes)
            pixmap = QPixmap()
            pixmap.loadFromData(chart_bytes)
            self.plot_image.setPixmap(pixmap.scaled(self.plot_image.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.context.last_chart_path = chart_path

        return {
            "analysis": analysis_tag,
            "column": column,
            "results": result_data,
            "explanation": explanation,
            "code": "\n".join(code_lines),
            "chart_path": chart_path,
        }

    def _build_explanation(self, analysis_tag: str, stats: Dict[str, Any]) -> str:
        lang = self.context.language
        if analysis_tag == "descriptive":
            tmpl = translate("explain.descriptive", lang)
            return tmpl.format(**stats)
        if analysis_tag == "t_test_one_sample":
            tmpl = translate("explain.ttest_one", lang)
            return tmpl.format(**stats)
        if analysis_tag == "t_test_two_sample":
            tmpl = translate("explain.ttest_two", lang)
            return tmpl.format(**stats)
        return ""

    def _display_results(self, results: Dict[str, Any]) -> None:
        stats = results["results"].get("statistics", {})
        lines = [f"{key}: {value}" for key, value in stats.items()]
        self.results_text.setText("\n".join(lines))
        self.explanation_text.setText(results.get("explanation", ""))
        self.code_text.setText(results.get("code", ""))

    def _report_context(self, results: Dict[str, Any]) -> Dict[str, Any]:
        lang = self.context.language
        return {
            "language": lang,
            "titles": {
                "title": translate("report.title", lang),
                "subtitle": translate("report.subtitle", lang),
            },
            "sections": {
                "overview": translate("label.results", lang),
                "statistics": translate("label.results", lang),
                "explanation": translate("label.explanation", lang),
                "code": translate("label.code", lang),
                "chart": translate("label.plot", lang),
            },
            "table_headers": {
                "metric": "Metric",
                "value": "Value",
            },
            "overview_text": results.get("explanation", ""),
            "statistics": results["results"].get("statistics", {}),
            "explanation": results.get("explanation", ""),
            "code": results.get("code", ""),
            "chart_path": results.get("chart_path"),
            "footer": "Generated locally",
        }

    def _update_ui_state(self) -> None:
        tag = self.analysis_combo.currentData()
        self.group_list.setEnabled(tag == "t_test_two_sample")
        self.reference_input.setEnabled(tag == "t_test_one_sample")

    # endregion


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
