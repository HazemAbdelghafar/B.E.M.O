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
              label: 'DASHBOARD',
              selected: currentSection == BemoSection.dashboard,
              onTap: () => onSectionTap(BemoSection.dashboard),
            ),
            const SizedBox(height: 8),
            _SidebarNav(
              iconAsset: 'assets/images/Idea.png',
              label: 'PROJECTS',
              selected: currentSection == BemoSection.projects,
              onTap: () => onSectionTap(BemoSection.projects),
            ),
            const SizedBox(height: 8),
            _SidebarNav(
              iconAsset: 'assets/images/At sign.png',
              label: 'E-MAIL',
              selected: currentSection == BemoSection.email,
              onTap: () => onSectionTap(BemoSection.email),
            ),
            const SizedBox(height: 8),
            _SidebarNav(
              iconAsset: 'assets/images/To Do List.png',
              label: 'TASKS',
              selected: currentSection == BemoSection.tasks,
              onTap: () => onSectionTap(BemoSection.tasks),
            ),
            const SizedBox(height: 8),
            _SidebarNav(
              iconAsset: 'assets/images/Calendar 28.png',
              label: 'CALENDAR',
              selected: currentSection == BemoSection.calendar,
              onTap: () => onSectionTap(BemoSection.calendar),
            ),
            const SizedBox(height: 8),
            _SidebarNav(
              iconAsset: 'assets/images/Cloud Folder.png',
              label: 'DRIVE',
              selected: currentSection == BemoSection.drive,
              onTap: () => onSectionTap(BemoSection.drive),
            ),
            const SizedBox(height: 8),
            _SidebarNav(
              iconAsset: 'assets/images/Smart Home Connection.png',
              label: 'SMART HOME',
              selected: currentSection == BemoSection.smartHome,
              onTap: () => onSectionTap(BemoSection.smartHome),
            ),
            const SizedBox(height: 8),
            _SidebarNav(
              iconAsset: 'assets/images/Chat.png',
              label: 'CHAT HISTORY',
              selected: currentSection == BemoSection.chatHistory,
              onTap: () => onSectionTap(BemoSection.chatHistory),
            ),
            const SizedBox(height: 8),
            _SidebarNav(
              iconAsset: 'assets/images/Notification.png',
              label: 'NOTIFICATIONS',
              selected: currentSection == BemoSection.notifications,
              onTap: () => onSectionTap(BemoSection.notifications),
            ),
            const SizedBox(height: 8),
            _SidebarNav(
              iconAsset: 'assets/images/Control Panel.png',
              label: 'SETTINGS',
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
              iconAsset: 'assets/images/Calendar 28.png',
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
              iconAsset: 'assets/images/Control Panel.png',
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
                      backgroundImage: AssetImage('assets/images/Robot - Inverted 1.png'),
                    ),
                  )
                : Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      CircleAvatar(
                        radius: 28,
                        backgroundImage: AssetImage('assets/images/Robot - Inverted 1.png'),
                      ),
                      const SizedBox(width: 16),
                      Text(
                        userName,
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
  final String label;
  final bool selected;
  final VoidCallback? onTap;
  const _SidebarNav({this.iconAsset, required this.label, this.selected = false, this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 10.0, horizontal: 32.0),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.start,
          children: [
            if (iconAsset != null)
              Image.asset(iconAsset!, height: 28, color: Colors.white),
            const SizedBox(width: 22),
            Text(
              label,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 18,
                color: selected ? Colors.amber : Colors.white,
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
  final String iconAsset;
  final bool selected;
  final VoidCallback? onTap;
  const _SidebarIconOnly({required this.iconAsset, this.selected = false, this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8.0),
        child: Center(
          child: Image.asset(iconAsset, height: 28, color: selected ? Colors.amber : Colors.white),
        ),
      ),
    );
  }
} 