import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout,
    QFileDialog, QComboBox, QLineEdit, QHBoxLayout, QWidget
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class DataVisualizationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Visualization App")
        self.setGeometry(100, 100, 800, 600)

        self.data = None

        self.main_widget = QWidget()
        self.layout = QVBoxLayout(self.main_widget)
        self.setCentralWidget(self.main_widget)

        self.add_components()

    def add_components(self):
        self.load_button = QPushButton("Load CSV")
        self.load_button.clicked.connect(self.load_data)
        self.layout.addWidget(self.load_button)

        self.stats_label = QLabel("No data loaded.")
        self.layout.addWidget(self.stats_label)

        self.chart_type_label = QLabel("Select Chart Type:")
        self.layout.addWidget(self.chart_type_label)

        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["Line Chart", "Histogram", "Pie Chart"])
        self.layout.addWidget(self.chart_type_combo)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.add_value_layout = QHBoxLayout()

        self.add_value_label = QLabel("Add Value:")
        self.add_value_layout.addWidget(self.add_value_label)

        self.add_value_input = QLineEdit()
        self.add_value_layout.addWidget(self.add_value_input)

        self.add_value_button = QPushButton("Add")
        self.add_value_button.clicked.connect(self.add_value)
        self.add_value_layout.addWidget(self.add_value_button)

        self.layout.addLayout(self.add_value_layout)

        self.plot_button = QPushButton("Plot Chart")
        self.plot_button.clicked.connect(self.plot_chart)
        self.layout.addWidget(self.plot_button)

    def load_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.data = pd.read_csv(file_path)
            self.update_stats()

    def update_stats(self):
        if self.data is not None:
            rows, cols = self.data.shape
            stats = f"Rows: {rows}, Columns: {cols}\n"
            for col in self.data.columns:
                if self.data[col].dtype in ['int64', 'float64']:
                    stats += f"{col}: Min={self.data[col].min()}, Max={self.data[col].max()}\n"
            self.stats_label.setText(stats)

    def plot_chart(self):
        if self.data is None:
            self.stats_label.setText("Please load a dataset first.")
            return

        chart_type = self.chart_type_combo.currentText()
        self.ax.clear()

        if chart_type == "Line Chart":
            if "Date" in self.data.columns and "Value1" in self.data.columns:
                self.data.plot(x="Date", y="Value1", ax=self.ax)
            else:
                self.stats_label.setText("Required columns: Date, Value1.")

        elif chart_type == "Histogram":
            if "Date" in self.data.columns and "Value2" in self.data.columns:
                self.ax.bar(self.data["Date"], self.data["Value2"])
            else:
                self.stats_label.setText("Required columns: Date, Value2.")

        elif chart_type == "Pie Chart":
            if "Category" in self.data.columns:
                self.data["Category"].value_counts().plot.pie(ax=self.ax, autopct='%1.1f%%')
            else:
                self.stats_label.setText("Required column: Category.")

        self.canvas.draw()

    def add_value(self):
        new_value = self.add_value_input.text()
        if not new_value:
            return

        try:
            new_value = float(new_value)
            if "Value1" in self.data.columns:
                new_row = pd.DataFrame([[new_value]], columns=["Value1"])
                self.data = pd.concat([self.data, new_row], ignore_index=True)
                self.update_stats()
            else:
                self.stats_label.setText("Cannot add value: 'Value1' column missing.")
        except ValueError:
            self.stats_label.setText("Invalid input. Please enter a numeric value.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = DataVisualizationApp()
    main_window.show()
    sys.exit(app.exec_())
