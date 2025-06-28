import '../widgets/fields.dart';
import '../utils/constants.dart';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../services/firebase_user_service.dart';
import '../services/websocket_service.dart';

//Todo: Chagne file name of the profile picture
//Todo: Save profile picture to firebase storage

class GettingStartedPage extends StatefulWidget {
  const GettingStartedPage({super.key});

  @override
  State<GettingStartedPage> createState() => _GettingStartedPageState();
}

class _GettingStartedPageState extends State<GettingStartedPage> {
  final _formKey = GlobalKey<FormState>();
  bool darkMode = true;
  bool obscureRobotId = true;
  bool useFullNameAsNickname = false;

  // Controllers
  final bioController = TextEditingController();
  final dobController = TextEditingController();
  final robotIdController = TextEditingController();
  final addressController = TextEditingController();
  final lastNameController = TextEditingController();
  final nicknameController = TextEditingController();
  final firstNameController = TextEditingController();
  final occupationController = TextEditingController();

  // Constants
  String? selectedImagePath;
  String? selectedFileName;
  String? selectedTitle = 'Eng.';
  String? selectedGender = 'Male';
  String selectedTheme = 'Device Default';
  String? selectedCountry = 'Device Default';
  String? selectedTimeZone = 'Device Default';
  List<bool> selectedThemes = [false, true, false];

  Future<void> _selectDate(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime(2003, 6, 23),
      firstDate: DateTime(1900, 1, 1),
      lastDate: DateTime.now(),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: ColorScheme.dark(
              primary: Color(0xFFEFEFEF),
              surface: Color(0xFF191919),
              onSurface: Colors.white,
            ),
          ),
          child: child!,
        );
      },
    );
    if (picked != null) {
      setState(() {
        dobController.text =
            "${picked.day.toString().padLeft(2, '0')}-${picked.month.toString().padLeft(2, '0')}-${picked.year}";
      });
    }
  }

  @override
  void initState() {
    super.initState();
    firstNameController.addListener(() {
      if (useFullNameAsNickname) {
        nicknameController.text =
            "${firstNameController.text} ${lastNameController.text}";
      }
    });
    lastNameController.addListener(() {
      if (useFullNameAsNickname) {
        nicknameController.text =
            "${firstNameController.text} ${lastNameController.text}";
      }
    });
    WebSocketService().connect();
  }

  @override
  void dispose() {
    bioController.dispose();
    dobController.dispose();
    addressController.dispose();
    robotIdController.dispose();
    lastNameController.dispose();
    nicknameController.dispose();
    firstNameController.dispose();
    occupationController.dispose();
    super.dispose();
  }

  Widget _buildThemeButton(
    BuildContext context,
    String label,
    bool selected,
    VoidCallback onPressed,
  ) {
    return Expanded(
      child: GestureDetector(
        onTap: onPressed,
        child: Container(
          height: 45,
          decoration: BoxDecoration(
            color: selected ? Color(0xFFEFEFEF) : Colors.transparent,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Color(0xFFEFEFEF), width: 1.5),
          ),
          alignment: Alignment.center,
          child: Text(
            label,
            style: TextStyle(
              fontFamily: 'Hyperion',
              fontWeight: FontWeight.bold,
              fontSize: 16,
              color: selected ? Color(0xFF191919) : Color(0xFFEFEFEF),
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final Map<String, dynamic> arguments =
        ModalRoute.of(context)!.settings.arguments as Map<String, dynamic>;
    final String uid = arguments['uid']!;
    final String idToken = arguments['idToken']!;
    final String email = arguments['email']!;

    return Scaffold(
      body: Stack(
        children: [
          // Background
          SizedBox.expand(
            child: Image.asset(
              'assets/images/getting_started_background.png',
              fit: BoxFit.cover,
            ),
          ),

          // Form container
          LayoutBuilder(
            builder: (context, constraints) {
              return SingleChildScrollView(
                // padding: EdgeInsets.all(24),
                child: Row(
                  children: [
                    // LEFT SIDE (3/4)
                    Container(
                      width: constraints.maxWidth * 0.75,
                      height: constraints.maxHeight,
                      padding: const EdgeInsets.all(15),
                      decoration: BoxDecoration(
                        color: Color(0xFF191919),
                        borderRadius: BorderRadius.only(
                          topRight: Radius.circular(24),
                          bottomRight: Radius.circular(24),
                        ),
                      ),
                      child: Form(
                        key: _formKey,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                            Text(
                              'getting started',
                              style: TextStyle(
                                fontFamily: 'Hyperion',
                                fontSize: 28,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFFEFEFEF),
                              ),
                            ),
                            Text(
                              'make BEMO your own',
                              style: TextStyle(
                                fontFamily: 'Hyperion',
                                fontSize: 16,
                                fontWeight: FontWeight.w700,
                                color: Color(0xAFEFEFEF),
                              ),
                            ),
                            const SizedBox(height: 20),

                            // Row 1: First name, Last name, Country, Time zone
                            Row(
                              children: [
                                Expanded(
                                  child: buildField(
                                    darkMode,
                                    'First Name',
                                    controller: firstNameController,
                                    hintText: 'mclovin',
                                    labelNote: "(don't lie)",
                                    required: true,
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: buildField(
                                    darkMode,
                                    'Last Name',
                                    controller: lastNameController,
                                    hintText: 'mcflurry',
                                    labelNote: "(also don't lie)",
                                    required: true,
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: buildDropdownField(
                                    darkMode: darkMode,
                                    label: 'Country',
                                    labelNote:
                                        "(a.k.a how fast is your internet)",
                                    value: selectedCountry,
                                    items: countryList,
                                    onChanged: (value) {
                                      setState(() {
                                        selectedCountry = value;
                                      });
                                    },
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: buildDropdownField(
                                    darkMode: darkMode,
                                    label: 'Time Zone',
                                    labelNote: "(just keep the device default)",
                                    value: selectedTimeZone,
                                    items: timeZoneList,
                                    onChanged: (value) {
                                      setState(() {
                                        selectedTimeZone = value;
                                      });
                                    },
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 10),
                            // Row 2: Nickname (+checkbox), Address
                            Row(
                              crossAxisAlignment:
                                  CrossAxisAlignment.start, // Align at the top
                              children: [
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      buildField(
                                        darkMode,
                                        'Nickname',
                                        labelNote:
                                            '(BEMO will address you using that name)',
                                        hintText: 'Cringy nickname maybe?',
                                        controller: nicknameController,
                                        required: useFullNameAsNickname
                                            ? false
                                            : true,
                                      ),
                                      Row(
                                        children: [
                                          Checkbox(
                                            value: useFullNameAsNickname,
                                            onChanged: (value) {
                                              setState(() {
                                                useFullNameAsNickname =
                                                    value ?? false;
                                                if (useFullNameAsNickname) {
                                                  nicknameController.text =
                                                      "${firstNameController.text} ${lastNameController.text}";
                                                } else {
                                                  nicknameController.text = "";
                                                }
                                              });
                                            },
                                          ),
                                          Text(
                                            "Just use my full name",
                                            style: TextStyle(
                                              color: Color(0xAFEFEFEF),
                                              fontFamily: 'Hyperion',
                                              fontWeight: FontWeight.w700,
                                              fontSize: 12,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: buildField(
                                    darkMode,
                                    'Address',
                                    labelNote: "(don't worry we won't dox you)",
                                    hintText:
                                        "3828 Piermont dr, Albuquerque, NM",
                                    controller: addressController,
                                    required: true,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 10),
                            // Row 3: Title, Occupation
                            Row(
                              children: [
                                Expanded(
                                  child: buildDropdownField(
                                    darkMode: darkMode,
                                    label: 'Title',
                                    labelNote: '(so you can feel special)',
                                    value: selectedTitle,
                                    items: titleList,
                                    onChanged: (value) {
                                      setState(() {
                                        selectedTitle = value;
                                      });
                                    },
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: buildField(
                                    darkMode,
                                    'Occupation',
                                    labelNote: '(don\'t be embarrassed)',
                                    hintText: 'dog food tester',
                                    controller: occupationController,
                                    required: true,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 10),
                            // Row 4: Gender + Date of Birth, Bio
                            Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Expanded(
                                  flex: 1,
                                  child: Column(
                                    children: [
                                      buildDropdownField(
                                        darkMode: darkMode,
                                        label: 'Gender',
                                        labelNote: '(just for analytics stuff)',
                                        value: selectedGender,
                                        items: genderList,
                                        onChanged: (value) {
                                          setState(() {
                                            selectedGender = value;
                                          });
                                        },
                                      ),
                                      const SizedBox(height: 12),
                                      GestureDetector(
                                        onTap: () => _selectDate(context),
                                        child: AbsorbPointer(
                                          child: buildField(
                                            darkMode,
                                            'date of birth',
                                            labelNote:
                                                '(don\'t worry this isn\'t ph)',
                                            controller: dobController,
                                            required: true,
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: buildMultilineField(
                                    darkMode,
                                    'bio',
                                    labelNote:
                                        '(tell us a bit about yourself...)',
                                    hintText:
                                        'I am a dog food tester and I love to eat dog food.',
                                    controller: bioController,
                                    required: false,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 10),
                            // Row 5: Robot ID, App Theme
                            Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Expanded(
                                  child: buildPasswordField(
                                    darkMode,
                                    'Robot ID',
                                    labelNote: '(provided with your device)',
                                    obscureText: obscureRobotId,
                                    toggle: () {
                                      setState(() {
                                        obscureRobotId = !obscureRobotId;
                                      });
                                    },
                                    controller: robotIdController,
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        'app theme',
                                        style: TextStyle(
                                          fontFamily: 'Hyperion',
                                          fontSize: 15,
                                          fontWeight: FontWeight.w700,
                                          color: Colors.white,
                                        ),
                                      ),
                                      const SizedBox(height: 6),
                                      Row(
                                        children: [
                                          _buildThemeButton(
                                            context,
                                            'light theme',
                                            selectedTheme == 'Light',
                                            () {
                                              setState(() {
                                                selectedTheme = 'Light';
                                              });
                                            },
                                          ),
                                          const SizedBox(width: 12),
                                          _buildThemeButton(
                                            context,
                                            'dark theme',
                                            selectedTheme == 'Dark',
                                            () {
                                              setState(() {
                                                selectedTheme = 'Dark';
                                              });
                                            },
                                          ),
                                          const SizedBox(width: 12),
                                          _buildThemeButton(
                                            context,
                                            'device default',
                                            selectedTheme == 'Device Default',
                                            () {
                                              setState(() {
                                                selectedTheme =
                                                    'Device Default';
                                              });
                                            },
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 10),
                            // Row 6: Profile Picture, Submit button
                            Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                // Profile Picture Picker
                                Expanded(
                                  flex: 1,
                                  child: buildProfilePicturePicker(
                                    darkMode: darkMode,
                                    imagePath: selectedImagePath,
                                    fileName: selectedFileName,
                                    onUpload: () async {
                                      FilePickerResult? result =
                                          await FilePicker.platform.pickFiles(
                                            type: FileType.image,
                                          );
                                      if (result != null) {
                                        setState(() {
                                          selectedImagePath =
                                              result.files.single.path!;
                                        });
                                      }
                                    },
                                  ),
                                ),
                                const SizedBox(width: 24),
                                // Submit Button
                                Expanded(
                                  flex: 1,
                                  child: Column(
                                    children: [
                                      const SizedBox(height: 43),
                                      SizedBox(
                                        height: 48,
                                        width: double.infinity,
                                        child: ElevatedButton(
                                          onPressed: () async {
                                            if (_formKey.currentState!
                                                .validate()) {
                                              await FirebaseUserService().saveUserData(
                                                uid: uid,
                                                idToken: idToken,
                                                data: {
                                                  "first_name":
                                                      firstNameController.text
                                                          .trim()[0]
                                                          .toUpperCase() +
                                                      firstNameController.text
                                                          .trim()
                                                          .substring(1),
                                                  "last_name":
                                                      lastNameController.text
                                                          .trim()[0]
                                                          .toUpperCase() +
                                                      lastNameController.text
                                                          .trim()
                                                          .substring(1),
                                                  "full_name":
                                                      "${firstNameController.text.trim()[0].toUpperCase() + firstNameController.text.trim().substring(1)} ${lastNameController.text.trim()[0].toUpperCase() + lastNameController.text.trim().substring(1)}",
                                                  'prefered_name':
                                                      useFullNameAsNickname
                                                      ? "${firstNameController.text.trim()[0].toUpperCase() + firstNameController.text.trim().substring(1)} ${lastNameController.text.trim()[0].toUpperCase() + lastNameController.text.trim().substring(1)}"
                                                      : nicknameController.text
                                                                .trim()[0]
                                                                .toUpperCase() +
                                                            nicknameController
                                                                .text
                                                                .trim()
                                                                .substring(1),
                                                  'email':
                                                      email, //Todo: Remove this and implement firebase user service function to fetch user data
                                                  "country": selectedCountry,
                                                  "timezone":
                                                      utcToIanaMap[selectedTimeZone] ??
                                                      'Africa/Cairo',
                                                  "nickname":
                                                      nicknameController.text
                                                          .trim()[0]
                                                          .toUpperCase() +
                                                      nicknameController.text
                                                          .trim()
                                                          .substring(1),
                                                  "address":
                                                      addressController.text,
                                                  "title": selectedTitle,
                                                  "occupation":
                                                      occupationController.text
                                                          .split('')
                                                          .map(
                                                            (e) =>
                                                                e.toUpperCase(),
                                                          )
                                                          .join(''),
                                                  "gender": selectedGender,
                                                  "bio": bioController.text,
                                                  "date_of_birth":
                                                      dobController.text,
                                                  'age':
                                                      '22', // Todo: Calculate age from date of birth
                                                  // 'age':
                                                  //     DateTime.now()
                                                  //         .difference(
                                                  //           DateTime.parse(
                                                  //             dobController
                                                  //                 .text,
                                                  //           ),
                                                  //         )
                                                  //         .inDays ~/
                                                  //     365,
                                                  "robot_id":
                                                      robotIdController.text,
                                                  "src_user_id":
                                                      robotIdController.text
                                                          .replaceAll(
                                                            'bemo',
                                                            'user',
                                                          ),
                                                  "theme": selectedTheme,
                                                },
                                              );

                                              Navigator.pushNamed(
                                                context,
                                                '/dashboard',
                                              );
                                            }
                                          },
                                          style: ElevatedButton.styleFrom(
                                            backgroundColor: Colors.white,
                                            shape: RoundedRectangleBorder(
                                              borderRadius:
                                                  BorderRadius.circular(12),
                                            ),
                                            padding: const EdgeInsets.symmetric(
                                              horizontal: 24,
                                            ),
                                          ),
                                          child: Text(
                                            'continue to greatness',
                                            style: TextStyle(
                                              color: Colors.black,
                                              fontFamily: 'Hyperion',
                                              fontSize: 16,
                                              fontWeight: FontWeight.bold,
                                            ),
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),

                    // RIGHT SIDE (1/4)
                    SizedBox(
                      width: constraints.maxWidth * 0.25,
                      height: constraints.maxHeight,
                      // padding: EdgeInsets.only(left: 24),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.start,
                        children: [
                          const SizedBox(height: 50),
                          Image.asset(
                            'assets/images/bemo_face.png',
                            height: 120,
                          ),
                          const SizedBox(height: 100),

                          Text(
                            'Customize your experience',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontFamily: 'Hyperion',
                              fontSize: 32,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'tailor your ai assistant to match your style, preferences, and habits.',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontFamily: 'Hyperion',
                              fontSize: 19,
                              fontWeight: FontWeight.w500,
                              color: Colors.white70,
                            ),
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'craft an assistant that fits your style—because no two users are the same.',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontFamily: 'Hyperion',
                              fontSize: 19,
                              fontWeight: FontWeight.w500,
                              color: Colors.white70,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}
