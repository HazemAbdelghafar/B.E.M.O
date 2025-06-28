import 'package:flutter/material.dart';

enum BemoSection {
  dashboard,
  projects,
  email,
  tasks,
  calendar,
  drive,
  smartHome,
  chatHistory,
  notifications,
  settings,
}

class CalendarDayIcon extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final int day = DateTime.now().day;
    return Container(
      width: 28,
      height: 28,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(6),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        mainAxisAlignment: MainAxisAlignment.start,
        children: [
          SizedBox(height: 2),
          Container(
            width: 16,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.black,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          SizedBox(height: 2),
          Text(
            day.toString(),
            style: const TextStyle(
              color: Colors.black,
              fontWeight: FontWeight.w900,
              fontSize: 11,
              fontFamily: 'Hyperion',
            ),
          ),
        ],
      ),
    );
  }
}

class BemoSidebar extends StatelessWidget {
  final bool collapsed;
  final VoidCallback onToggle;
  final BemoSection currentSection;
  final Function(BemoSection) onSectionTap;
  final String userName;

  const BemoSidebar({
    Key? key,
    required this.collapsed,
    required this.onToggle,
    required this.currentSection,
    required this.onSectionTap,
    required this.userName,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      width: collapsed ? 70 : 300,
      height: 980,
      decoration: const BoxDecoration(
        color: Color(0xFF191919),
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(30),
          bottomLeft: Radius.circular(30),
        ),
      ),
      child: Column(
        children: [
          const SizedBox(height: 48),
          GestureDetector(
            onTap: onToggle,
            child: Container(
              width: collapsed ? 48 : 200,
              height: 60,
              alignment: Alignment.center,
              child: collapsed
                  ? Image.asset(
                      'assets/images/Robot - Inverted 1.png',
                      fit: BoxFit.contain,
                      height: 48,
                    )
                  : Image.asset(
                      'assets/images/Logo 2 - Transparent Inverted 1 1.png',
                      fit: BoxFit.contain,
                      height: 48,
                    ),
            ),
          ),
          if (!collapsed) ...[
            const SizedBox(height: 48),
            _SidebarNav(
              iconAsset: 'assets/images/Control Panel.png',
              label: 'dashboard',
              selected: currentSection == BemoSection.dashboard,
              onTap: () => onSectionTap(BemoSection.dashboard),
            ),
            const SizedBox(height: 8),
            _SidebarNav(
              iconAsset: 'assets/images/Idea.png',
              label: 'projects',
              selected: currentSection == BemoSection.projects,
              onTap: () => onSectionTap(BemoSection.projects),
            ),
            const SizedBox(height: 8),
            _SidebarNav(
              iconAsset: 'assets/images/At sign.png',
              label: 'e-mail',
              selected: currentSection == BemoSection.email,
              onTap: () => onSectionTap(BemoSection.email),
            ),
            const SizedBox(height: 8),
            _SidebarNav(
              iconAsset: 'assets/images/To Do List.png',
              label: 'tasks',
              selected: currentSection == BemoSection.tasks,
              onTap: () => onSectionTap(BemoSection.tasks),
            ),
            const SizedBox(height: 8),
            _SidebarNav(
              iconAsset: null,
              customIcon: CalendarDayIcon(),
              label: 'calendar',
              selected: currentSection == BemoSection.calendar,
              onTap: () => onSectionTap(BemoSection.calendar),
            ),
            const SizedBox(height: 8),
            _SidebarNav(
              iconAsset: 'assets/images/Cloud Folder.png',
              label: 'drive',
              selected: currentSection == BemoSection.drive,
              onTap: () => onSectionTap(BemoSection.drive),
            ),
            const SizedBox(height: 8),
            _SidebarNav(
              iconAsset: 'assets/images/Smart Home Connection.png',
              label: 'smart home',
              selected: currentSection == BemoSection.smartHome,
              onTap: () => onSectionTap(BemoSection.smartHome),
            ),
            const SizedBox(height: 8),
            _SidebarNav(
              iconAsset: 'assets/images/Chat.png',
              label: 'chat history',
              selected: currentSection == BemoSection.chatHistory,
              onTap: () => onSectionTap(BemoSection.chatHistory),
            ),
            const SizedBox(height: 8),
            _SidebarNav(
              iconAsset: 'assets/images/Notification.png',
              label: 'notifications',
              selected: currentSection == BemoSection.notifications,
              onTap: () => onSectionTap(BemoSection.notifications),
            ),
            const SizedBox(height: 8),
            _SidebarNav(
              iconAsset: 'assets/Images/Services.png',
              label: 'settings',
              selected: currentSection == BemoSection.settings,
              onTap: () => onSectionTap(BemoSection.settings),
            ),
          ] else ...[
            const SizedBox(height: 32),
            _SidebarIconOnly(
              iconAsset: 'assets/images/Control Panel.png',
              selected: currentSection == BemoSection.dashboard,
              onTap: () => onSectionTap(BemoSection.dashboard),
            ),
            const SizedBox(height: 16),
            _SidebarIconOnly(
              iconAsset: 'assets/images/Idea.png',
              selected: currentSection == BemoSection.projects,
              onTap: () => onSectionTap(BemoSection.projects),
            ),
            const SizedBox(height: 16),
            _SidebarIconOnly(
              iconAsset: 'assets/images/At sign.png',
              selected: currentSection == BemoSection.email,
              onTap: () => onSectionTap(BemoSection.email),
            ),
            const SizedBox(height: 16),
            _SidebarIconOnly(
              iconAsset: 'assets/images/To Do List.png',
              selected: currentSection == BemoSection.tasks,
              onTap: () => onSectionTap(BemoSection.tasks),
            ),
            const SizedBox(height: 16),
            _SidebarIconOnly(
              iconAsset: null,
              customIcon: CalendarDayIcon(),
              selected: currentSection == BemoSection.calendar,
              onTap: () => onSectionTap(BemoSection.calendar),
            ),
            const SizedBox(height: 16),
            _SidebarIconOnly(
              iconAsset: 'assets/images/Cloud Folder.png',
              selected: currentSection == BemoSection.drive,
              onTap: () => onSectionTap(BemoSection.drive),
            ),
            const SizedBox(height: 16),
            _SidebarIconOnly(
              iconAsset: 'assets/images/Smart Home Connection.png',
              selected: currentSection == BemoSection.smartHome,
              onTap: () => onSectionTap(BemoSection.smartHome),
            ),
            const SizedBox(height: 16),
            _SidebarIconOnly(
              iconAsset: 'assets/images/Chat.png',
              selected: currentSection == BemoSection.chatHistory,
              onTap: () => onSectionTap(BemoSection.chatHistory),
            ),
            const SizedBox(height: 16),
            _SidebarIconOnly(
              iconAsset: 'assets/images/Notification.png',
              selected: currentSection == BemoSection.notifications,
              onTap: () => onSectionTap(BemoSection.notifications),
            ),
            const SizedBox(height: 16),
            _SidebarIconOnly(
              iconAsset: 'assets/Images/Services.png',
              selected: currentSection == BemoSection.settings,
              onTap: () => onSectionTap(BemoSection.settings),
            ),
          ],
          const Spacer(),
          Padding(
            padding: const EdgeInsets.only(bottom: 32.0),
            child: collapsed
                ? Center(
                    child: CircleAvatar(
                      radius: 28,
                      backgroundImage:
                          AssetImage('assets/images/Robot - Inverted 1.png'),
                    ),
                  )
                : Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      CircleAvatar(
                        radius: 28,
                        backgroundImage:
                            AssetImage('assets/images/Robot - Inverted 1.png'),
                      ),
                      const SizedBox(width: 16),
                      Text(
                        userName.toLowerCase(),
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                          color: Color.fromRGBO(255, 255, 255, 0.7),
                        ),
                      ),
                    ],
                  ),
          ),
        ],
      ),
    );
  }
}

class _SidebarNav extends StatelessWidget {
  final String? iconAsset;
  final Widget? customIcon;
  final String label;
  final bool selected;
  final VoidCallback? onTap;
  const _SidebarNav(
      {this.iconAsset,
      this.customIcon,
      required this.label,
      this.selected = false,
      this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 10.0, horizontal: 32.0),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.start,
          children: [
            if (selected)
              Container(
                width: 4,
                height: 32,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            if (selected) const SizedBox(width: 12),
            if (customIcon != null)
              customIcon!
            else if (iconAsset != null)
              Image.asset(iconAsset!, height: 28, color: Colors.white),
            const SizedBox(width: 22),
            Text(
              label.toLowerCase(),
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 18,
                color: Colors.white,
                letterSpacing: 1.2,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SidebarIconOnly extends StatelessWidget {
  final String? iconAsset;
  final Widget? customIcon;
  final bool selected;
  final VoidCallback? onTap;
  const _SidebarIconOnly(
      {this.iconAsset, this.selected = false, this.onTap, this.customIcon});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8.0),
        child: Center(
          child: customIcon ??
              (iconAsset != null
                  ? Image.asset(iconAsset!, height: 28, color: Colors.white)
                  : SizedBox.shrink()),
        ),
      ),
    );
  }
}
