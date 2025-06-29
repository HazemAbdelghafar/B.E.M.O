// import 'package:flutter/material.dart';
// import '../widgets/fields.dart';
// import '../services/firebase_rest_auth.dart';
// import '../services/local_storage_service.dart';

// class LoginScreen extends StatefulWidget {
//   const LoginScreen({super.key});

//   @override
//   State<LoginScreen> createState() => _LoginScreenState();
// }

// class _LoginScreenState extends State<LoginScreen> {
//   final _formKey = GlobalKey<FormState>();
//   final TextEditingController emailController = TextEditingController();
//   final TextEditingController passwordController = TextEditingController();

//   final emailKey = GlobalKey<FormFieldState>();

//   bool _obscurePassword = true;
//   bool darkMode = true;
//   bool submitted = false;
//   final FirebaseRestAuth _auth = FirebaseRestAuth();

//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       body: Stack(
//         children: [
//           // Background image
//           SizedBox.expand(
//             child: Image.asset(
//               'assets/images/signup_login_background.png',
//               fit: BoxFit.cover,
//             ),
//           ),

//           // Signup form
//           Center(
//             child: Container(
//               height: 600,
//               width: 500,
//               padding: const EdgeInsets.all(24),
//               decoration: BoxDecoration(
//                 color: darkMode ? Color(0xFF191919) : Color(0xFFEFEFEF),
//                 borderRadius: BorderRadius.circular(24),
//               ),
//               child: Form(
//                 key: _formKey,
//                 child: Column(
//                   mainAxisSize: MainAxisSize.min,
//                   children: [
//                     const SizedBox(height: 12),
//                     Text(
//                       'Welcome back!',
//                       style: TextStyle(
//                         fontFamily: 'Hyperion',
//                         fontSize: 28,
//                         color: darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
//                         fontWeight: FontWeight.w700,
//                       ),
//                     ),
//                     Text(
//                       "you know what to do",
//                       style: TextStyle(
//                         fontFamily: 'Hyperion',
//                         fontSize: 16,
//                         fontWeight: FontWeight.w700,
//                         color: darkMode ? Color(0xB0EFEFEF) : Color(0xFF191919),
//                       ),
//                     ),

//                     const SizedBox(height: 50),

//                     // Email
//                     buildField(
//                       darkMode,
//                       'email address',
//                       hintText: 'cringyusername@example.com',
//                       labelNote: "(required)",
//                       required: true,
//                       controller: emailController,
//                     ),
//                     const SizedBox(height: 12),

//                     // Password
//                     buildPasswordField(
//                       darkMode,
//                       'password',
//                       labelNote: '(required)',
//                       obscureText: _obscurePassword,
//                       toggle: () => setState(() {
//                         _obscurePassword = !_obscurePassword;
//                       }),
//                       controller: passwordController,
//                     ),
//                     Row(
//                       mainAxisAlignment: MainAxisAlignment.start,
//                       children: [
//                         Text(
//                           "we've all been there",
//                           style: TextStyle(
//                             fontFamily: 'Hyperion',
//                             fontWeight: FontWeight.w700,
//                             fontSize: 10,
//                             color: darkMode
//                                 ? Color(0xD9EFEFEF)
//                                 : Color(0xBB101010),
//                           ),
//                         ),
//                         TextButton(
//                           style: TextButton.styleFrom(
//                             padding: EdgeInsets.only(left: 5),
//                           ),
//                           onPressed: () async {
//                             final isValid =
//                                 emailKey.currentState?.validate() ?? false;
//                             if (!isValid) return;

//                             final email = emailController.text.trim();

//                             final result = await _auth.sendPasswordResetEmail(
//                               email,
//                             );

//                             if (result.containsKey('error')) {
//                               showDialog(
//                                 context: context,
//                                 builder: (_) => AlertDialog(
//                                   title: Text("Error"),
//                                   content: Text(result['error']['message']),
//                                 ),
//                               );
//                             } else {
//                               showDialog(
//                                 context: context,
//                                 builder: (_) => AlertDialog(
//                                   title: Text("Success"),
//                                   content: Text(
//                                     "Password reset email sent to $email.",
//                                   ),
//                                 ),
//                               );
//                             }
//                           },

//                           child: Text(
//                             'reset password',
//                             style: TextStyle(
//                               decoration: TextDecoration.underline,
//                               decorationColor: darkMode
//                                   ? Color(0xFFEFEFEF)
//                                   : Color(0xFF101010),
//                               fontFamily: 'Hyperion',
//                               fontWeight: FontWeight.w700,
//                               fontSize: 11,
//                               color: darkMode
//                                   ? Color(0xFFEFEFEF)
//                                   : Color(0xFF101010),
//                             ),
//                           ),
//                         ),
//                       ],
//                     ),
//                     const SizedBox(height: 12),

//                     // Login Button
//                     SizedBox(
//                       width: double.infinity,
//                       child: ElevatedButton(
//                         style: ElevatedButton.styleFrom(
//                           backgroundColor: darkMode
//                               ? Color(0xFFEFEFEF)
//                               : Color(0xFF191919),
//                           foregroundColor: darkMode
//                               ? Colors.black
//                               : Color(0xFFEFEFEF),
//                           padding: const EdgeInsets.symmetric(vertical: 14),
//                           shape: RoundedRectangleBorder(
//                             borderRadius: BorderRadius.circular(12),
//                           ),
//                         ),
//                         onPressed: () async {
//                           setState(() {
//                             submitted = true;
//                           });

//                           if (_formKey.currentState!.validate()) {
//                             final result = await _auth.signIn(
//                               emailController.text.trim(),
//                               passwordController.text.trim(),
//                             );

//                             print(result);
//                             if (result.containsKey('error')) {
//                               // Clear all stored data on login failure
//                               await LocalStorageService.clearAllData();

//                               showDialog(
//                                 context: context,
//                                 builder: (_) => AlertDialog(
//                                   title: Text("Login Failed"),
//                                   content: Text(result['error']['message']),
//                                 ),
//                               );
//                             } else {
//                               final String uid = result['localId'];
//                               final String idToken = result['idToken'];
//                               print('uid: $uid');
//                               print('idToken: $idToken');
//                               final String email =
//                                   await _auth.getUserEmail(idToken) ?? '';
//                               print('email: $email');

//                               // Save credentials locally
//                               await LocalStorageService.saveUserCredentials(
//                                 uid: uid,
//                                 idToken: idToken,
//                                 email: email,
//                               );

//                               Navigator.pushNamed(context, '/dashboard');
//                             }
//                           }
//                         },
//                         child: Text(
//                           'login',
//                           style: TextStyle(
//                             fontFamily: 'Hyperion',
//                             fontSize: 22,
//                             fontWeight: FontWeight.w700,
//                             color: darkMode
//                                 ? Color(0xFF191919)
//                                 : Color(0xFFEFEFEF),
//                           ),
//                         ),
//                       ),
//                     ),

//                     const SizedBox(height: 12),

//                     // OR with Google / GitHub / Apple
//                     Text(
//                       'or the easier options',
//                       style: TextStyle(
//                         fontFamily: 'Hyperion',
//                         fontWeight: FontWeight.w700,
//                         fontSize: 15,
//                         color: darkMode ? Color(0xB3EFEFEF) : Color(0xFF191919),
//                       ),
//                     ),

//                     const SizedBox(height: 12),

//                     Row(
//                       mainAxisAlignment: MainAxisAlignment.center,
//                       children: [
//                         buildIconButton(darkMode, 'assets/images/Google.png'),
//                         const SizedBox(width: 16),
//                         buildIconButton(darkMode, 'assets/images/Apple.png'),
//                         const SizedBox(width: 16),
//                         buildIconButton(
//                           darkMode,
//                           'assets/images/Microsoft.png',
//                         ),
//                       ],
//                     ),

//                     const SizedBox(height: 8),

//                     // Login text
//                     Row(
//                       mainAxisAlignment: MainAxisAlignment.center,
//                       children: [
//                         Text(
//                           "not already a part of the bemo club?",
//                           style: TextStyle(
//                             fontFamily: 'Hyperion',
//                             fontWeight: FontWeight.w700,
//                             fontSize: 13,
//                             color: darkMode
//                                 ? Color(0xD9EFEFEF)
//                                 : Color(0xFF191919),
//                           ),
//                         ),
//                         TextButton(
//                           onPressed: () {
//                             Navigator.pushNamed(context, '/signup');
//                           },
//                           child: Text(
//                             'sign up',
//                             style: TextStyle(
//                               decoration: TextDecoration.underline,
//                               decorationColor: darkMode
//                                   ? Color(0xFFEFEFEF)
//                                   : Color(0xFF191919),
//                               fontFamily: 'Hyperion',
//                               fontWeight: FontWeight.w700,
//                               fontSize: 13,
//                               color: darkMode
//                                   ? Color(0xFFEFEFEF)
//                                   : Color(0xFF191919),
//                             ),
//                           ),
//                         ),
//                       ],
//                     ),
//                     TextButton(
//                       onPressed: () {
//                         // Handle terms and conditions tap
//                       },
//                       child: Text(
//                         'terms and conditions',
//                         style: TextStyle(
//                           fontFamily: 'Hyperion',
//                           fontWeight: FontWeight.w700,
//                           fontSize: 10,
//                           decoration: TextDecoration.underline,
//                           decorationColor: darkMode
//                               ? Color(0xFFEFEFEF)
//                               : Color(0xFF191919),
//                           color: darkMode
//                               ? Color(0xFFEFEFEF)
//                               : Color(0xFF191919),
//                         ),
//                       ),
//                     ),
//                   ],
//                 ),
//               ),
//             ),
//           ),
//         ],
//       ),
//     );
//   }
// }

import 'package:flutter/material.dart';
import '../widgets/fields.dart';
import '../services/firebase_user_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController emailController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();

  final emailKey = GlobalKey<FormFieldState>();

  bool _obscurePassword = true;
  bool darkMode = true;
  bool submitted = false;
  final FirebaseUserService _auth = FirebaseUserService();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // Background image
          SizedBox.expand(
            child: Image.asset(
              'assets/images/signup_login_background.png',
              fit: BoxFit.cover,
            ),
          ),

          // Signup form
          Center(
            child: Container(
              height: 600,
              width: 500,
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: darkMode ? Color(0xFF191919) : Color(0xFFEFEFEF),
                borderRadius: BorderRadius.circular(24),
              ),
              child: Form(
                key: _formKey,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const SizedBox(height: 12),
                    Text(
                      'Welcome back!',
                      style: TextStyle(
                        fontFamily: 'Hyperion',
                        fontSize: 28,
                        color: darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    Text(
                      "you know what to do",
                      style: TextStyle(
                        fontFamily: 'Hyperion',
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        color: darkMode ? Color(0xB0EFEFEF) : Color(0xFF191919),
                      ),
                    ),

                    const SizedBox(height: 50),

                    // Email
                    buildField(
                      darkMode,
                      'email address',
                      hintText: 'cringyusername@example.com',
                      labelNote: "(required)",
                      required: true,
                      controller: emailController,
                      key: emailKey,
                    ),
                    const SizedBox(height: 12),

                    // Password
                    buildPasswordField(
                      darkMode,
                      'password',
                      labelNote: '(required)',
                      obscureText: _obscurePassword,
                      toggle: () => setState(() {
                        _obscurePassword = !_obscurePassword;
                      }),
                      controller: passwordController,
                    ),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.start,
                      children: [
                        Text(
                          "we've all been there",
                          style: TextStyle(
                            fontFamily: 'Hyperion',
                            fontWeight: FontWeight.w700,
                            fontSize: 10,
                            color: darkMode
                                ? Color(0xD9EFEFEF)
                                : Color(0xBB101010),
                          ),
                        ),
                        TextButton(
                          style: TextButton.styleFrom(
                            padding: EdgeInsets.only(left: 5),
                          ),
                          onPressed: () async {
                            final isValid =
                                emailKey.currentState?.validate() ?? false;
                            if (!isValid) return;

                            final email = emailController.text.trim();

                            final result = await _auth.sendPasswordResetEmail(
                              email,
                            );

                            if (result.containsKey('error')) {
                              showDialog(
                                context: context,
                                builder: (_) => AlertDialog(
                                  title: Text("Error"),
                                  content: Text(result['error']['message']),
                                ),
                              );
                            } else {
                              showDialog(
                                context: context,
                                builder: (_) => AlertDialog(
                                  title: Text("Success"),
                                  content: Text(
                                    "Password reset email sent to $email.",
                                  ),
                                ),
                              );
                            }
                          },

                          child: Text(
                            'reset password',
                            style: TextStyle(
                              decoration: TextDecoration.underline,
                              decorationColor: darkMode
                                  ? Color(0xFFEFEFEF)
                                  : Color(0xFF101010),
                              fontFamily: 'Hyperion',
                              fontWeight: FontWeight.w700,
                              fontSize: 11,
                              color: darkMode
                                  ? Color(0xFFEFEFEF)
                                  : Color(0xFF101010),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),

                    // Login Button
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: darkMode
                              ? Color(0xFFEFEFEF)
                              : Color(0xFF191919),
                          foregroundColor: darkMode
                              ? Colors.black
                              : Color(0xFFEFEFEF),
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        onPressed: () async {
                          setState(() {
                            submitted = true;
                          });

                          if (_formKey.currentState!.validate()) {
                            final result = await _auth.signIn(
                              emailController.text.trim(),
                              passwordController.text.trim(),
                            );

                            print(result);
                            if (result.containsKey('error')) {
                              showDialog(
                                context: context,
                                builder: (_) => AlertDialog(
                                  title: Text("Login Failed"),
                                  content: Text(result['error']['message']),
                                ),
                              );
                            } else {
                              final String uid = result['localId'];
                              final String idToken = result['idToken'];

                              Navigator.pushNamed(
                                context,
                                '/dashboard',
                                arguments: {
                                  'uid': uid,
                                  'idToken': idToken,
                                  'email': emailController.text.trim(),
                                },
                              );
                            }
                          }
                        },
                        child: Text(
                          'login',
                          style: TextStyle(
                            fontFamily: 'Hyperion',
                            fontSize: 22,
                            fontWeight: FontWeight.w700,
                            color: darkMode
                                ? Color(0xFF191919)
                                : Color(0xFFEFEFEF),
                          ),
                        ),
                      ),
                    ),

                    const SizedBox(height: 12),

                    // OR with Google / GitHub / Apple
                    Text(
                      'or the easier options',
                      style: TextStyle(
                        fontFamily: 'Hyperion',
                        fontWeight: FontWeight.w700,
                        fontSize: 15,
                        color: darkMode ? Color(0xB3EFEFEF) : Color(0xFF191919),
                      ),
                    ),

                    const SizedBox(height: 12),

                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        buildIconButton(darkMode, 'assets/images/Google.png'),
                        const SizedBox(width: 16),
                        buildIconButton(darkMode, 'assets/images/Apple.png'),
                        const SizedBox(width: 16),
                        buildIconButton(
                          darkMode,
                          'assets/images/Microsoft.png',
                        ),
                      ],
                    ),

                    const SizedBox(height: 8),

                    // Login text
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          "not already a part of the bemo club?",
                          style: TextStyle(
                            fontFamily: 'Hyperion',
                            fontWeight: FontWeight.w700,
                            fontSize: 13,
                            color: darkMode
                                ? Color(0xD9EFEFEF)
                                : Color(0xFF191919),
                          ),
                        ),
                        TextButton(
                          onPressed: () {
                            Navigator.pushNamed(context, '/signup');
                          },
                          child: Text(
                            'sign up',
                            style: TextStyle(
                              decoration: TextDecoration.underline,
                              decorationColor: darkMode
                                  ? Color(0xFFEFEFEF)
                                  : Color(0xFF191919),
                              fontFamily: 'Hyperion',
                              fontWeight: FontWeight.w700,
                              fontSize: 13,
                              color: darkMode
                                  ? Color(0xFFEFEFEF)
                                  : Color(0xFF191919),
                            ),
                          ),
                        ),
                      ],
                    ),
                    TextButton(
                      onPressed: () {
                        // Handle terms and conditions tap
                      },
                      child: Text(
                        'terms and conditions',
                        style: TextStyle(
                          fontFamily: 'Hyperion',
                          fontWeight: FontWeight.w700,
                          fontSize: 10,
                          decoration: TextDecoration.underline,
                          decorationColor: darkMode
                              ? Color(0xFFEFEFEF)
                              : Color(0xFF191919),
                          color: darkMode
                              ? Color(0xFFEFEFEF)
                              : Color(0xFF191919),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
