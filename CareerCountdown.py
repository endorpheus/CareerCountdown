import sys
import os
import json

from PyQt6.QtWidgets import (
    QWidget, QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, 
    QProgressBar, QStatusBar, QMenuBar, QDialog, 
    QHBoxLayout, QDateEdit, QSpinBox, QDialogButtonBox, QInputDialog, QListWidget,
    QMessageBox
)
from PyQt6.QtCore import QDate, QDateTime, QTimer, QTime, Qt
from PyQt6.QtGui import QAction, QIcon

#from flashing_label import FlashingLabel

PROFILES_FILE = 'profiles.json'

class ProfileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Profile")
        self.setModal(True)

        layout = QVBoxLayout()

        self.birthdateEdit = QDateEdit(QDate(1982, 1, 17))
        self.careerStartEdit = QDateEdit(QDate(1998, 6, 1))
        self.retirementAgeSpinBox = QSpinBox()
        self.retirementAgeSpinBox.setRange(1, 100)
        self.retirementAgeSpinBox.setValue(65)

        layout.addWidget(QLabel("Birthdate:"))
        layout.addWidget(self.birthdateEdit)
        layout.addWidget(QLabel("Career Start Date:"))
        layout.addWidget(self.careerStartEdit)
        layout.addWidget(QLabel("Retirement Age:"))
        layout.addWidget(self.retirementAgeSpinBox)

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox)

        self.setLayout(layout)

    def getSettings(self):
        return {
            'birthdate': self.birthdateEdit.date().toString('yyyy-MM-dd'),
            'career_start': self.careerStartEdit.date().toString('yyyy-MM-dd'),
            'retirement_age': self.retirementAgeSpinBox.value()
        }

    def setSettings(self, settings):
        self.birthdateEdit.setDate(QDate.fromString(settings['birthdate'], 'yyyy-MM-dd'))
        self.careerStartEdit.setDate(QDate.fromString(settings['career_start'], 'yyyy-MM-dd'))
        self.retirementAgeSpinBox.setValue(settings['retirement_age'])

class ProfileSelectionDialog(QDialog):
    def __init__(self, profiles, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Profile")
        self.setModal(True)

        layout = QVBoxLayout()

        self.listWidget = QListWidget()
        self.listWidget.addItems(profiles.keys())
        layout.addWidget(self.listWidget)

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox)

        self.setLayout(layout)

    def getSelectedProfile(self):
        return self.listWidget.currentItem().text() if self.listWidget.currentItem() else None


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)        
        self.setWindowFlags(Qt.WindowType.Window | 
                            Qt.WindowType.WindowSystemMenuHint | 
                            Qt.WindowType.WindowMinimizeButtonHint | 
                            Qt.WindowType.WindowCloseButtonHint)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)

        self.setWindowTitle("About")
        self.setStyleSheet("background-color: #210530; color: white;")
        self.setWindowOpacity(0.85)

        layout = QVBoxLayout()
    
        # Enable dragging
        self.m_dragPos = None

        # Load the custom icon
        icon_path = os.path.join(os.path.dirname(__file__), './icons/calendar.png')
        if os.path.exists(icon_path):
            iconLabel = QLabel()
            iconLabel.setPixmap(QIcon(icon_path).pixmap(64, 64))
            layout.addWidget(iconLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        else:
            print(f"Warning: Icon file not found at {icon_path}")
        
        layout.addWidget(QLabel("Career Countdown"), alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(QLabel("Version 1.2"), alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(QLabel("by Ryon Shane Hall"), alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(QLabel("endorpheus@gmail.com"), alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(QLabel("created: 202409040245"), alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(QLabel("modified: 202409110927"), alignment=Qt.AlignmentFlag.AlignCenter)
        
        closeButton = QPushButton("Close")
        closeButton.clicked.connect(self.close)

        layout.addWidget(closeButton)
        self.setLayout(layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.m_dragPos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.m_dragPos)
            event.accept()


class CareerCountdownWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.profiles = self.loadProfiles()
        self.currentProfile = 'default'
        self.loadSettings()

        self.retirementDate = self.birthdate.addYears(self.retirementAge)

        self.setWindowTitle("Career Countdown")
        
        # Load and set the icon
        icon_path = os.path.join(os.path.dirname(__file__), './icons/calendar.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"Warning: Icon file not found at {icon_path}")

        # Create widgets for displaying information
        
        self.ageLabel = QLabel()
        self.careerStartLabel = QLabel()
        self.timeInCareerLabel = QLabel()
        self.retirementDateLabel = QLabel()
        self.yearsRemainingLabel = QLabel()
        self.timeRemainingLabel = QLabel()
        self.daysSinceLastAnniversaryLabel = QLabel()
        self.nextAnniversaryLabel = QLabel()
        self.progressBar = QProgressBar()

        # Colorize the retirement date label
        self.retirementDateLabel.setStyleSheet("color: blue;")

        # Set up layouts
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(5, 5, 5, 5)

        # Add widgets to layout
        mainLayout.addWidget(self.ageLabel)
        mainLayout.addWidget(self.careerStartLabel)
        mainLayout.addWidget(self.timeInCareerLabel)
        mainLayout.addWidget(self.retirementDateLabel)
        mainLayout.addWidget(self.yearsRemainingLabel)
        mainLayout.addWidget(self.timeRemainingLabel)
        mainLayout.addWidget(self.daysSinceLastAnniversaryLabel)
        mainLayout.addWidget(self.nextAnniversaryLabel)
        mainLayout.addWidget(self.progressBar)

        # Configure the central widget
        centralWidget = QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

        # Set up the status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Set up the menu bar
        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)

        # Create Settings menu
        settingsMenu = self.menuBar.addMenu("Settings")

        # Add actions to Settings menu
        editProfileAction = QAction("Edit Current Profile", self)
        editProfileAction.triggered.connect(self.openProfileDialog)
        settingsMenu.addAction(editProfileAction)

        newProfileAction = QAction("New Profile", self)
        newProfileAction.triggered.connect(self.newProfile)
        settingsMenu.addAction(newProfileAction)

        loadProfileAction = QAction("Load Profile", self)
        loadProfileAction.triggered.connect(self.loadProfile)
        settingsMenu.addAction(loadProfileAction)

        saveProfileAction = QAction("Save Current Profile", self)
        saveProfileAction.triggered.connect(self.saveCurrentProfile)
        settingsMenu.addAction(saveProfileAction)

        deleteProfileAction = QAction("Delete Profile", self)
        deleteProfileAction.triggered.connect(self.deleteProfile)
        settingsMenu.addAction(deleteProfileAction)

        # About menu
        aboutAction = QAction("About", self)
        aboutAction.triggered.connect(self.openAboutDialog)
        self.menuBar.addAction(aboutAction)

        # Initialize the countdown
        self.updateRetirementData()

        # Set up a timer to refresh the countdown every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateRetirementData)
        self.timer.start(1000)  # 1 second

    def openProfileDialog(self):
        dialog = ProfileDialog(self)
        dialog.setSettings(self.getSettings())
        if dialog.exec():
            settings = dialog.getSettings()
            self.setSettings(settings)
            self.saveProfiles()
            self.updateRetirementData()

    def openAboutDialog(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def getSettings(self):
        return {
            'birthdate': self.birthdate.toString('yyyy-MM-dd'),
            'career_start': self.careerStart.toString('yyyy-MM-dd'),
            'retirement_age': self.retirementAge
        }

    def setSettings(self, settings):
        self.birthdate = QDate.fromString(settings['birthdate'], 'yyyy-MM-dd')
        self.careerStart = QDate.fromString(settings['career_start'], 'yyyy-MM-dd')
        self.retirementAge = settings['retirement_age']
        self.retirementDate = self.birthdate.addYears(self.retirementAge)

    def loadProfiles(self):
        try:
            with open(PROFILES_FILE, 'r') as file:
                profiles = json.load(file)
            
            # Ensure the loaded profiles are valid
            if not isinstance(profiles, dict):
                raise ValueError("Invalid profiles format. Delete profiles.json and try again.")
            
            return profiles
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            # If the file doesn't exist, is corrupt, or has an invalid format, start with a default profile
            return {'default': {
                'birthdate': '1982-01-17',
                'career_start': '1998-06-01',
                'retirement_age': 65
            }}

    def saveProfiles(self):
        try:
            with open(PROFILES_FILE, 'w') as file:
                json.dump(self.profiles, file, indent=4, sort_keys=True)
        except IOError as e:
            QMessageBox.critical(self, "Error", f"Failed to save profiles: {e}")

    def loadSettings(self):
        settings = self.profiles[self.currentProfile]
        self.setSettings(settings)

    def loadProfile(self):
        dialog = ProfileSelectionDialog(self.profiles, self)
        if dialog.exec():
            selected_profile = dialog.getSelectedProfile()
            if selected_profile:
                self.currentProfile = selected_profile
                self.loadSettings()
                self.updateRetirementData()

    def newProfile(self):
        name, ok = QInputDialog.getText(self, "New Profile", "Enter new profile name:")
        if ok and name:
            if name in self.profiles:
                QMessageBox.warning(self, "Profile Exists", f"Profile '{name}' already exists.")
            else:
                self.currentProfile = name
                self.profiles[name] = self.getSettings()
                self.saveProfiles()
                self.updateRetirementData()

    def saveCurrentProfile(self):
        self.profiles[self.currentProfile] = self.getSettings()
        self.saveProfiles()
        QMessageBox.information(self, "Profile Saved", f"Profile '{self.currentProfile}' has been saved.")

    def deleteProfile(self):
        if len(self.profiles) <= 1:
            QMessageBox.warning(self, "Cannot Delete", "You must have at least one profile.")
            return

        dialog = ProfileSelectionDialog(self.profiles, self)
        dialog.setWindowTitle("Select Profile to Delete")
        if dialog.exec():
            profile_to_delete = dialog.getSelectedProfile()
            if profile_to_delete:
                confirm = QMessageBox.question(self, "Confirm Deletion", 
                                               f"Are you sure you want to delete the profile '{profile_to_delete}'?",
                                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if confirm == QMessageBox.StandardButton.Yes:
                    del self.profiles[profile_to_delete]
                    if self.currentProfile == profile_to_delete:
                        self.currentProfile = next(iter(self.profiles))
                        self.loadSettings()
                    self.saveProfiles()
                    self.updateRetirementData()
                    QMessageBox.information(self, "Profile Deleted", f"Profile '{profile_to_delete}' has been deleted.")

    def updateRetirementData(self):
        currentDate = QDate.currentDate()
        currentDateTime = QDateTime.currentDateTime()

        # Calculate age
        age = currentDate.year() - self.birthdate.year()
        if (currentDate.month() < self.birthdate.month()) or \
           (currentDate.month() == self.birthdate.month() and currentDate.day() < self.birthdate.day()):
            age -= 1

        # Calculate time spent in career
        timeInCareer = self.careerStart.daysTo(currentDate)
        yearsInCareer = timeInCareer // 365
        monthsInCareer = (timeInCareer % 365) // 30

        # Check if career has ended
        careerEnded = currentDate >= self.retirementDate

        if careerEnded:
            remainingYears = remainingMonths = remainingDays = remainingHours = remainingMinutes = remainingSeconds = 0
        else:
            # Calculate the time remaining until retirement
            retirementDateTime = QDateTime(self.retirementDate, QTime(0, 0))
            remainingSeconds = currentDateTime.secsTo(retirementDateTime)

            # Calculate years, months, days, hours, minutes, and seconds
            remainingYears = self.retirementDate.year() - currentDate.year()
            remainingMonths = self.retirementDate.month() - currentDate.month()
            remainingDays = self.retirementDate.day() - currentDate.day()

            if remainingDays < 0:
                remainingMonths -= 1
                remainingDays += currentDate.daysInMonth()
            
            if remainingMonths < 0:
                remainingYears -= 1
                remainingMonths += 12

            remainingHours = remainingSeconds // 3600 % 24
            remainingMinutes = remainingSeconds // 60 % 60
            remainingSeconds = remainingSeconds % 60

        # Calculate years remaining with higher precision for progress bar
        totalDays = self.careerStart.daysTo(self.retirementDate)
        daysPassed = self.careerStart.daysTo(currentDate)
        yearsRemaining = (totalDays - daysPassed) / 365.25

        # Calculate days since last anniversary
        lastAnniversary = QDate(currentDate.year(), self.careerStart.month(), self.careerStart.day())
        if currentDate < lastAnniversary:
            lastAnniversary = QDate(currentDate.year() - 1, self.careerStart.month(), self.careerStart.day())

        daysSinceLastAnniversary = lastAnniversary.daysTo(currentDate)
        nextAnniversary = lastAnniversary.addYears(1)
        daysToNextAnniversary = currentDate.daysTo(nextAnniversary)

        # Progress bar calculation
        totalCareerDays = self.careerStart.daysTo(self.retirementDate)
        currentCareerDays = self.careerStart.daysTo(currentDate)
        progress = min((currentCareerDays / totalCareerDays) * 100, 100)  # Ensure progress doesn't exceed 100%
        self.progressBar.setValue(int(progress))

        # Update labels
        self.retirementDateLabel.setText(f"Retirement Date: {self.retirementDate.toString('yyyy-MM-dd')}")
        self.ageLabel.setText(f"Age: {age} years (Born: {self.birthdate.toString('MM/dd/yyyy')})")
        self.timeInCareerLabel.setText(f"Time in Career: {yearsInCareer} years, {monthsInCareer} months")
        
        if careerEnded:    
            self.yearsRemainingLabel.setText("Career Ended")
            self.timeRemainingLabel.setText("Congratulations on your retirement!")
            
            #colorize timeRemainingLabel to green
            self.timeRemainingLabel.setStyleSheet("color: green;")
            self.yearsRemainingLabel.setStyleSheet("color: green;")
        else:
            self.yearsRemainingLabel.setText(f"Years Remaining: {yearsRemaining:.2f}")
            self.timeRemainingLabel.setText(
                f"Time Remaining: {remainingYears} years, {remainingMonths} months, {remainingDays} days, "
                f"{remainingHours} hours, {remainingMinutes} minutes, {remainingSeconds} seconds"
            )
            # default color
            self.timeRemainingLabel.setStyleSheet("color: black;")
            self.yearsRemainingLabel.setStyleSheet("color: black;")

        self.careerStartLabel.setText(f"Career Start Date: {self.careerStart.toString('yyyy-MM-dd')}")
        self.daysSinceLastAnniversaryLabel.setText(f"Days Since Last Anniversary: {daysSinceLastAnniversary}")
        self.nextAnniversaryLabel.setText(f"Next Anniversary: {nextAnniversary.toString('yyyy-MM-dd')}, "
                                          f"{daysToNextAnniversary} days remaining")

        # Update the status bar with the current date and time, profile name, and accurate percentage
        statusMessage = f"Current Profile: {self.currentProfile} | Progress: {progress:.2f}% | "
        statusMessage += "Career Ended" if careerEnded else f"{QDateTime.currentDateTime().toString()}"
        self.statusBar.showMessage(statusMessage)

        # Adjust window to fixed size of 432x233
        self.resize(432, 233)

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CareerCountdownWindow()
    window.show()    
    sys.exit(app.exec())
