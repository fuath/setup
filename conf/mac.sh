#!/bin/sh

### trackpad settings ###
for key in com.apple.AppleMultitouchTrackpad com.apple.driver.AppleBluetoothMultitouch.trackpad; do
    defaults write $key Clicking -boolean True # touch to click

    # enable *both* methods of right clicking
    defaults write $key TrackpadRightClick -boolean True # two finger tap
    defaults write $key TrackpadCornerSecondaryClick -integer 2 # pushing to click in right corner

    # disable "smart zoom" because it puts a delay on two-finger-tap right click
    defaults write $key TrackpadTwoFingerDoubleTapGesture -boolean False

    defaults write $key TrackpadThreeFingerDrag -boolean True
done


# disable dashboard
defaults write com.apple.dashboard mcx-disabled -boolean True

# http://www.defaults-write.com/enable-highlight-hover-effect-for-grid-view-stacks/
defaults write com.apple.dock mouse-over-hilite-stack -boolean True


# hot corners
# Possible values:
#  0: no-op
#  2: Mission Control
#  3: Show application windows
#  4: Desktop
#  5: Start screen saver
#  6: Disable screen saver
#  7: Dashboard
# 10: Put display to sleep
# 11: Launchpad
# 12: Notification Center

# bottom left: sleep
defaults write com.apple.dock wvous-bl-corner -integer 10
defaults write com.apple.dock wvous-bl-modifier -integer 0

# bottom right: application windows
defaults write com.apple.dock wvous-br-corner -integer 3
defaults write com.apple.dock wvous-br-modifier -integer 0

# top left: mission control
defaults write com.apple.dock wvous-tl-corner -integer 2
defaults write com.apple.dock wvous-tl-modifier -integer 0

# top right: desktop
defaults write com.apple.dock wvous-tr-corner -integer 4
defaults write com.apple.dock wvous-tr-modifier -integer 0


# finder
defaults write com.apple.finder ShowPathbar -boolean True
defaults write com.apple.finder ShowStatusBar -boolean True

# show battery % in menubar
defaults write com.apple.menuextra.battery ShowPercent -boolean True

# key repeat rate and delay
defaults write NSGlobalDomain InitialKeyRepeat -integer 10
defaults write NSGlobalDomain KeyRepeat -integer 2
