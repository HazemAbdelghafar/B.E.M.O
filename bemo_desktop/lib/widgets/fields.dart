import 'package:flutter/material.dart';
import '../utils/constants.dart';
import 'dart:io';

Widget buildField(
  bool darkMode,
  String label, {
  String? hintText,
  String? labelNote,
  bool required = false,
  bool obscureText = false,
  TextEditingController? controller,
  Key? key,
}) {
  return _FieldWithInternalError(
    darkMode: darkMode,
    label: label,
    hintText: hintText,
    labelNote: labelNote,
    required: required,
    obscureText: obscureText,
    controller: controller,
    key: key,
  );
}

class _FieldWithInternalError extends StatefulWidget {
  final bool darkMode;
  final String label;
  final String? hintText;
  final String? labelNote;
  final bool required;
  final bool obscureText;
  final TextEditingController? controller;
  final Key? key;

  const _FieldWithInternalError({
    required this.darkMode,
    required this.label,
    this.hintText,
    this.labelNote,
    this.required = false,
    this.obscureText = false,
    this.controller,
    this.key,
  });

  @override
  State<_FieldWithInternalError> createState() =>
      _FieldWithInternalErrorState();
}

class _FieldWithInternalErrorState extends State<_FieldWithInternalError> {
  String? errorText;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(
              widget.label,
              style: TextStyle(
                fontFamily: 'Hyperion',
                fontSize: 15,
                fontWeight: FontWeight.w700,
                color: widget.darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
              ),
            ),
            if (widget.labelNote != null) ...[
              const SizedBox(width: 6),
              Text(
                widget.labelNote!,
                style: TextStyle(
                  fontFamily: 'Hyperion',
                  fontSize: 8,
                  fontWeight: FontWeight.w700,
                  color: widget.darkMode
                      ? Color(0x80EFEFEF)
                      : Color(0xFF191919),
                ),
              ),
            ],
          ],
        ),
        const SizedBox(height: 6),
        TextFormField(
          key: widget.key,
          controller: widget.controller,
          obscureText: widget.obscureText,
          decoration: InputDecoration(
            hintText: errorText ?? widget.hintText,
            hintStyle: TextStyle(
              fontFamily: 'Hyperion',
              fontSize: 15,
              fontWeight: FontWeight.w700,
              color: errorText != null
                  ? Colors.red
                  : (widget.darkMode ? Color(0x8CEFEFEF) : Color(0x60191919)),
            ),
            errorText: errorText != null ? '' : null,
            errorStyle: const TextStyle(height: 0, fontSize: 0),
            filled: true,
            fillColor: Colors.transparent,
            contentPadding: const EdgeInsets.symmetric(
              vertical: 14,
              horizontal: 12,
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(
                color: errorText != null
                    ? Colors.red
                    : (widget.darkMode ? Color(0x80EFEFEF) : Color(0x80191919)),
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(
                color: errorText != null
                    ? Colors.red
                    : (widget.darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919)),
              ),
            ),
          ),
          style: TextStyle(
            color: widget.darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
            fontFamily: 'Hyperion',
            fontWeight: FontWeight.w700,
            fontSize: 15,
          ),
          validator: widget.required
              ? (value) {
                  if (value == null || value.isEmpty) {
                    setState(() {
                      errorText = 'required';
                    });
                    return ''; // Avoid default Flutter error box
                  }
                  setState(() {
                    errorText = null;
                  });
                  return null;
                }
              : null,
        ),
      ],
    );
  }
}

// class _FieldWithInternalError extends StatefulWidget {
//   final bool darkMode;
//   final String label;
//   final String? hintText;
//   final String? labelNote;
//   final bool required;
//   final bool obscureText;
//   final TextEditingController? controller;

//   const _FieldWithInternalError({
//     required this.darkMode,
//     required this.label,
//     this.hintText,
//     this.labelNote,
//     this.required = false,
//     this.obscureText = false,
//     this.controller,
//   });

//   @override
//   State<_FieldWithInternalError> createState() =>
//       _FieldWithInternalErrorState();
// }

// class _FieldWithInternalErrorState extends State<_FieldWithInternalError> {
//   String? errorText;

//   @override
//   Widget build(BuildContext context) {
//     return Column(
//       crossAxisAlignment: CrossAxisAlignment.start,
//       children: [
//         Row(
//           crossAxisAlignment: CrossAxisAlignment.end,
//           children: [
//             Text(
//               widget.label,
//               style: TextStyle(
//                 fontFamily: 'Hyperion',
//                 fontSize: 15,
//                 fontWeight: FontWeight.w700,
//                 color: widget.darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
//               ),
//             ),
//             if (widget.labelNote != null) ...[
//               const SizedBox(width: 6),
//               Text(
//                 widget.labelNote!,
//                 style: TextStyle(
//                   fontFamily: 'Hyperion',
//                   fontSize: 8,
//                   fontWeight: FontWeight.w700,
//                   color: widget.darkMode
//                       ? Color(0x80EFEFEF)
//                       : Color(0xFF191919),
//                 ),
//               ),
//             ],
//           ],
//         ),
//         const SizedBox(height: 6),
//         TextFormField(
//           controller: widget.controller,
//           obscureText: widget.obscureText,
//           decoration: InputDecoration(
//             hintText: errorText ?? widget.hintText,
//             hintStyle: TextStyle(
//               fontFamily: 'Hyperion',
//               fontSize: 15,
//               fontWeight: FontWeight.w700,
//               color: errorText != null
//                   ? Colors.red
//                   : (widget.darkMode ? Color(0x8CEFEFEF) : Color(0x60191919)),
//             ),
//             filled: true,
//             fillColor: Colors.transparent,
//             contentPadding: const EdgeInsets.symmetric(
//               vertical: 14,
//               horizontal: 12,
//             ),
//             enabledBorder: OutlineInputBorder(
//               borderRadius: BorderRadius.circular(12),
//               borderSide: BorderSide(
//                 color: errorText != null
//                     ? Colors.red
//                     : (widget.darkMode ? Color(0x80EFEFEF) : Color(0x80191919)),
//               ),
//             ),
//             focusedBorder: OutlineInputBorder(
//               borderRadius: BorderRadius.circular(12),
//               borderSide: BorderSide(
//                 color: errorText != null
//                     ? Colors.red
//                     : (widget.darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919)),
//               ),
//             ),
//           ),
//           style: TextStyle(
//             color: widget.darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
//             fontFamily: 'Hyperion',
//             fontWeight: FontWeight.w700,
//             fontSize: 15,
//           ),
//           validator: widget.required
//               ? (value) {
//                   if (value == null || value.isEmpty) {
//                     setState(() {
//                       errorText = 'required';
//                     });
//                     return '';
//                   }
//                   setState(() {
//                     errorText = null;
//                   });
//                   return null;
//                 }
//               : null,
//         ),
//       ],
//     );
//   }
// }

Widget buildPasswordField(
  bool darkMode,
  String label, {
  String? labelNote,
  required bool obscureText,
  required VoidCallback toggle,
  TextEditingController? controller,
}) {
  return _PasswordFieldWithInternalError(
    darkMode: darkMode,
    label: label,
    labelNote: labelNote,
    obscureText: obscureText,
    toggle: toggle,
    controller: controller,
  );
}

class _PasswordFieldWithInternalError extends StatefulWidget {
  final bool darkMode;
  final String label;
  final String? labelNote;
  final bool obscureText;
  final VoidCallback toggle;
  final TextEditingController? controller;

  const _PasswordFieldWithInternalError({
    required this.darkMode,
    required this.label,
    this.labelNote,
    required this.obscureText,
    required this.toggle,
    this.controller,
  });

  @override
  State<_PasswordFieldWithInternalError> createState() =>
      _PasswordFieldWithInternalErrorState();
}

class _PasswordFieldWithInternalErrorState
    extends State<_PasswordFieldWithInternalError> {
  String? errorText;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(
              widget.label,
              style: TextStyle(
                color: widget.darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
                fontFamily: 'Hyperion',
                fontWeight: FontWeight.w700,
                fontSize: 15,
              ),
            ),
            if (widget.labelNote != null) ...[
              const SizedBox(width: 6),
              Text(
                widget.labelNote!,
                style: TextStyle(
                  fontFamily: 'Hyperion',
                  fontWeight: FontWeight.w700,
                  fontSize: 8,
                  color: widget.darkMode
                      ? const Color(0x80EFEFEF)
                      : const Color(0xFF191919),
                ),
              ),
            ],
          ],
        ),
        const SizedBox(height: 6),
        TextFormField(
          controller: widget.controller,
          obscureText: widget.obscureText,
          decoration: InputDecoration(
            hintText: errorText ?? '●●●●●●●●',
            hintStyle: TextStyle(
              fontFamily: 'Hyperion',
              fontWeight: FontWeight.w700,
              fontSize: 15,
              color: errorText != null
                  ? Colors.red
                  : (widget.darkMode ? Color(0x61EFEFEF) : Color(0x61191919)),
            ),
            errorText: errorText != null ? '' : null,
            errorStyle: const TextStyle(height: 0, fontSize: 0),
            suffixIcon: IconButton(
              onPressed: widget.toggle,
              icon: Image.asset(
                'assets/images/obscure_icon.png',
                height: 30,
                width: 30,
                color: widget.darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
              ),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(
                color: errorText != null
                    ? Colors.red
                    : (widget.darkMode ? Color(0x80EFEFEF) : Color(0x80191919)),
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(
                color: errorText != null
                    ? Colors.red
                    : (widget.darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919)),
              ),
            ),
            contentPadding: const EdgeInsets.symmetric(
              vertical: 14,
              horizontal: 12,
            ),
          ),
          style: TextStyle(
            color: widget.darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
            fontFamily: 'Hyperion',
            fontWeight: FontWeight.w700,
            fontSize: 15,
          ),
          validator: (value) {
            if (value == null || value.isEmpty) {
              setState(() {
                errorText = 'required';
              });
              return ''; // suppress external error text rendering
            }
            setState(() {
              errorText = null;
            });
            return null;
          },
        ),
      ],
    );
  }
}

// class _PasswordFieldWithInternalErrorState
//     extends State<_PasswordFieldWithInternalError> {
//   String? errorText;

//   @override
//   Widget build(BuildContext context) {
//     return Column(
//       crossAxisAlignment: CrossAxisAlignment.start,
//       children: [
//         Row(
//           crossAxisAlignment: CrossAxisAlignment.end,
//           children: [
//             Text(
//               widget.label,
//               style: TextStyle(
//                 color: widget.darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
//                 fontFamily: 'Hyperion',
//                 fontWeight: FontWeight.w700,
//                 fontSize: 15,
//               ),
//             ),
//             if (widget.labelNote != null) ...[
//               const SizedBox(width: 6),
//               Text(
//                 widget.labelNote!,
//                 style: TextStyle(
//                   fontFamily: 'Hyperion',
//                   fontWeight: FontWeight.w700,
//                   fontSize: 8,
//                   color: widget.darkMode
//                       ? const Color(0x80EFEFEF)
//                       : const Color(0xFF191919),
//                 ),
//               ),
//             ],
//           ],
//         ),
//         const SizedBox(height: 6),
//         TextFormField(
//           controller: widget.controller,
//           obscureText: widget.obscureText,
//           decoration: InputDecoration(
//             hintText: errorText ?? '●●●●●●●●',
//             hintStyle: TextStyle(
//               fontFamily: 'Hyperion',
//               fontWeight: FontWeight.w700,
//               color: errorText != null
//                   ? Colors.red
//                   : (widget.darkMode ? Color(0x60EFEFEF) : Color(0x61191919)),
//             ),
//             suffixIcon: IconButton(
//               onPressed: widget.toggle,
//               icon: Image.asset(
//                 'assets/images/obscure_icon.png',
//                 height: 30,
//                 width: 30,
//                 color: widget.darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
//               ),
//             ),
//             enabledBorder: OutlineInputBorder(
//               borderRadius: BorderRadius.circular(12),
//               borderSide: BorderSide(
//                 color: errorText != null
//                     ? Colors.red
//                     : (widget.darkMode ? Color(0x80EFEFEF) : Color(0x80191919)),
//               ),
//             ),
//             focusedBorder: OutlineInputBorder(
//               borderRadius: BorderRadius.circular(12),
//               borderSide: BorderSide(
//                 color: errorText != null
//                     ? Colors.red
//                     : (widget.darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919)),
//               ),
//             ),
//             contentPadding: const EdgeInsets.symmetric(
//               vertical: 14,
//               horizontal: 12,
//             ),
//           ),
//           style: TextStyle(
//             color: widget.darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
//             fontFamily: 'Hyperion',
//             fontWeight: FontWeight.w700,
//             fontSize: 15,
//           ),
//           validator: (value) {
//             if (value == null || value.isEmpty) {
//               setState(() {
//                 errorText = 'required';
//               });
//               return '';
//             }
//             setState(() {
//               errorText = null;
//             });
//             return null;
//           },
//         ),
//       ],
//     );
//   }
// }

Widget buildIconButton(bool darkMode, String assetPath) {
  return GestureDetector(
    onTap: () {},
    child: Container(
      height: 45,
      width: 45,
      decoration: BoxDecoration(
        color: darkMode ? Colors.white : Colors.black,
        borderRadius: BorderRadius.circular(12), // Rounded square
        boxShadow: [
          BoxShadow(
            color: darkMode ? Colors.black12 : Colors.white12,
            blurRadius: 4,
            offset: Offset(0, 2),
          ),
        ],
      ),
      padding: const EdgeInsets.all(10),
      child: Image.asset(
        assetPath,
        fit: BoxFit.cover,
        color: darkMode ? Colors.black : Colors.white,
      ),
    ),
  );
}

Widget buildTextField({
  required String label,
  required TextEditingController controller,
  bool isRequired = false,
}) {
  return TextFormField(
    controller: controller,
    decoration: InputDecoration(labelText: label, border: OutlineInputBorder()),
    validator: isRequired
        ? (value) =>
              value == null || value.isEmpty ? '$label is required' : null
        : null,
  );
}

Widget buildDropdown<T>({
  required String label,
  required T? value,
  required List<DropdownMenuItem<T>> items,
  required Function(T?) onChanged,
}) {
  return InputDecorator(
    decoration: InputDecoration(labelText: label, border: OutlineInputBorder()),
    child: DropdownButtonHideUnderline(
      child: DropdownButton<T>(
        value: value,
        items: items,
        onChanged: onChanged,
      ),
    ),
  );
}

// --- Dropdown for Title ---
Widget buildTitleDropdown(
  bool darkMode, {
  String? selected,
  Function(String?)? onChanged,
}) {
  return Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(
        'Title',
        style: TextStyle(
          fontFamily: 'Hyperion',
          fontSize: 15,
          fontWeight: FontWeight.w700,
          color: darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
        ),
      ),
      const SizedBox(height: 6),
      DropdownButtonFormField<String>(
        value: selected,
        onChanged: onChanged,
        items: titleList
            .map(
              (title) => DropdownMenuItem<String>(
                value: title,
                child: Text(
                  title,
                  style: TextStyle(
                    fontFamily: 'Hyperion',
                    fontWeight: FontWeight.w700,
                    fontSize: 14,
                    color: darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
                  ),
                ),
              ),
            )
            .toList(),
        decoration: InputDecoration(
          filled: true,
          fillColor: Colors.transparent,
          contentPadding: const EdgeInsets.symmetric(
            vertical: 14,
            horizontal: 12,
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide(
              color: darkMode ? Color(0x80EFEFEF) : Color(0x80191919),
            ),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide(
              color: darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
            ),
          ),
        ),
      ),
    ],
  );
}

// --- Dropdown for Gender ---
Widget buildGenderDropdown(
  bool darkMode, {
  String? selected,
  Function(String?)? onChanged,
}) {
  return Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(
        'Gender',
        style: TextStyle(
          fontFamily: 'Hyperion',
          fontSize: 15,
          fontWeight: FontWeight.w700,
          color: darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
        ),
      ),
      const SizedBox(height: 6),
      DropdownButtonFormField<String>(
        value: selected,
        onChanged: onChanged,
        items: genderList
            .map(
              (gender) => DropdownMenuItem<String>(
                value: gender,
                child: Text(
                  gender,
                  style: TextStyle(
                    fontFamily: 'Hyperion',
                    fontWeight: FontWeight.w700,
                    fontSize: 14,
                    color: darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
                  ),
                ),
              ),
            )
            .toList(),
        decoration: InputDecoration(
          filled: true,
          fillColor: Colors.transparent,
          contentPadding: const EdgeInsets.symmetric(
            vertical: 14,
            horizontal: 12,
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide(
              color: darkMode ? Color(0x80EFEFEF) : Color(0x80191919),
            ),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide(
              color: darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
            ),
          ),
        ),
      ),
    ],
  );
}

Widget buildDropdownField({
  required bool darkMode,
  required String label,
  String? labelNote,
  required String? value,
  required List<String> items,
  required void Function(String?) onChanged,
}) {
  return Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Text(
            label,
            style: TextStyle(
              fontFamily: 'Hyperion',
              fontSize: 15,
              fontWeight: FontWeight.w700,
              color: darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
            ),
          ),
          if (labelNote != null) ...[
            const SizedBox(width: 6),
            Text(
              labelNote,
              style: TextStyle(
                fontFamily: 'Hyperion',
                fontSize: 8,
                fontWeight: FontWeight.w700,
                color: darkMode ? Color(0x80EFEFEF) : Color(0x80191919),
              ),
            ),
          ],
        ],
      ),
      const SizedBox(height: 6),
      DropdownButtonFormField<String>(
        value: value,
        onChanged: onChanged,
        items: items
            .map(
              (item) => DropdownMenuItem<String>(
                value: item,
                child: Text(
                  item,
                  overflow: TextOverflow.fade,
                  softWrap: true,
                  maxLines: 1,
                  style: TextStyle(
                    fontFamily: 'Hyperion',
                    fontWeight: FontWeight.w700,
                    fontSize: 14,
                    color: darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
                  ),
                ),
              ),
            )
            .toList(),
        decoration: InputDecoration(
          filled: true,
          fillColor: Colors.transparent,
          contentPadding: const EdgeInsets.symmetric(
            vertical: 14,
            horizontal: 12,
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide(
              color: darkMode ? Color(0x80EFEFEF) : Color(0x80191919),
            ),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide(
              color: darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
            ),
          ),
        ),
        dropdownColor: darkMode ? Color(0xFF2C2C2C) : Colors.white,
        iconEnabledColor: darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
        style: TextStyle(
          overflow: TextOverflow.ellipsis,
          fontFamily: 'Hyperion',
          fontWeight: FontWeight.w700,
          fontSize: 14,
          color: darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
        ),
        validator: (value) {
          if (value == null || value.isEmpty) {
            return 'Required';
          }
          return null;
        },
      ),
    ],
  );
}

Widget buildMultilineField(
  bool darkMode,
  String label, {
  String? hintText,
  String? labelNote,
  bool required = false,
  TextEditingController? controller,
}) {
  return Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Text(
            label,
            style: TextStyle(
              fontFamily: 'Hyperion',
              fontSize: 15,
              fontWeight: FontWeight.w700,
              color: darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
            ),
          ),
          if (labelNote != null) ...[
            const SizedBox(width: 6),
            Text(
              labelNote,
              style: TextStyle(
                fontFamily: 'Hyperion',
                fontSize: 8,
                fontWeight: FontWeight.w700,
                color: darkMode ? Color(0x80EFEFEF) : Color(0xFF191919),
              ),
            ),
          ],
        ],
      ),
      const SizedBox(height: 6),
      TextFormField(
        controller: controller,
        maxLines: 5,
        decoration: InputDecoration(
          hintText: hintText,
          hintStyle: TextStyle(
            fontFamily: 'Hyperion',
            fontSize: 14,
            fontWeight: FontWeight.w700,
            color: darkMode ? Color(0x8CEFEFEF) : Color(0x60191919),
          ),
          filled: true,
          fillColor: Colors.transparent,
          contentPadding: const EdgeInsets.all(12),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide(
              color: darkMode ? Color(0x80EFEFEF) : Color(0x80191919),
            ),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide(
              color: darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
            ),
          ),
        ),
        style: TextStyle(
          color: darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
          fontFamily: 'Hyperion',
          fontWeight: FontWeight.w700,
          fontSize: 15,
        ),
        validator: required
            ? (value) {
                if (value == null || value.isEmpty) {
                  return 'required';
                }
                return null;
              }
            : null,
      ),
    ],
  );
}

Widget buildProfilePicturePicker({
  required bool darkMode,
  required String? imagePath,
  required String? fileName,
  required VoidCallback onUpload,
}) {
  return Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Text(
            'Profile Picture',
            style: TextStyle(
              fontFamily: 'Hyperion',
              fontSize: 15,
              fontWeight: FontWeight.w700,
              color: darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
            ),
          ),
          const SizedBox(width: 6),
          Text(
            "(say cheeeeese)",
            style: TextStyle(
              fontFamily: 'Hyperion',
              fontSize: 8,
              fontWeight: FontWeight.w700,
              color: darkMode ? Color(0x80EFEFEF) : Color(0xFF191919),
            ),
          ),
        ],
      ),
      const SizedBox(height: 6),
      Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.white, width: 1.2),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          children: [
            // Profile image
            ClipRRect(
              borderRadius: BorderRadius.circular(10),
              child: imagePath != null
                  ? Image.file(
                      File(imagePath),
                      height: 60,
                      width: 60,
                      fit: BoxFit.cover,
                    )
                  : Container(
                      height: 60,
                      width: 60,
                      color: Colors.grey.shade700,
                      child: Icon(Icons.person, color: Colors.white),
                    ),
            ),
            const SizedBox(width: 12),
            // File name
            Expanded(
              child: Text(
                fileName ?? 'No image selected',
                style: TextStyle(
                  fontFamily: 'Hyperion',
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  color: Colors.white70,
                ),
              ),
            ),
            const SizedBox(width: 12),
            // Upload button
            ElevatedButton.icon(
              onPressed: onUpload,
              style: ElevatedButton.styleFrom(
                backgroundColor: Color(0xFFEFEFEF),
                foregroundColor: Color(0xFF191919),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
              ),
              icon: Icon(Icons.upload, size: 20),
              label: Text(
                'Upload Image',
                style: TextStyle(
                  fontFamily: 'Hyperion',
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                ),
              ),
            ),
          ],
        ),
      ),
    ],
  );
}

// import 'dart:io';
// import 'package:flutter/material.dart';

// /// =======================
// ///     TEXT FIELD BUILDER
// /// =======================

// Widget buildField(
//   bool darkMode,
//   String label, {
//   String? hintText,
//   String? labelNote,
//   bool required = false,
//   bool obscureText = false,
//   TextEditingController? controller,
// }) {
//   return _FieldWithInternalError(
//     darkMode: darkMode,
//     label: label,
//     hintText: hintText,
//     labelNote: labelNote,
//     required: required,
//     obscureText: obscureText,
//     controller: controller,
//   );
// }

// class _FieldWithInternalError extends StatefulWidget {
//   final bool darkMode;
//   final String label;
//   final String? hintText;
//   final String? labelNote;
//   final bool required;
//   final bool obscureText;
//   final TextEditingController? controller;

//   const _FieldWithInternalError({
//     required this.darkMode,
//     required this.label,
//     this.hintText,
//     this.labelNote,
//     this.required = false,
//     this.obscureText = false,
//     this.controller,
//   });

//   @override
//   State<_FieldWithInternalError> createState() =>
//       _FieldWithInternalErrorState();
// }

// class _FieldWithInternalErrorState extends State<_FieldWithInternalError> {
//   String? errorText;

//   @override
//   Widget build(BuildContext context) {
//     return Column(
//       crossAxisAlignment: CrossAxisAlignment.start,
//       children: [
//         Row(
//           crossAxisAlignment: CrossAxisAlignment.end,
//           children: [
//             Text(
//               widget.label,
//               style: TextStyle(
//                 fontFamily: 'Hyperion',
//                 fontSize: 15,
//                 fontWeight: FontWeight.w700,
//                 color: widget.darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
//               ),
//             ),
//             if (widget.labelNote != null) ...[
//               const SizedBox(width: 6),
//               Text(
//                 widget.labelNote!,
//                 style: TextStyle(
//                   fontFamily: 'Hyperion',
//                   fontSize: 8,
//                   fontWeight: FontWeight.w700,
//                   color: widget.darkMode
//                       ? Color(0x80EFEFEF)
//                       : Color(0xFF191919),
//                 ),
//               ),
//             ],
//           ],
//         ),
//         const SizedBox(height: 6),
//         TextFormField(
//           controller: widget.controller,
//           obscureText: widget.obscureText,
//           decoration: InputDecoration(
//             hintText: errorText ?? widget.hintText,
//             hintStyle: TextStyle(
//               fontFamily: 'Hyperion',
//               fontSize: 15,
//               fontWeight: FontWeight.w700,
//               color: errorText != null
//                   ? Colors.red
//                   : (widget.darkMode ? Color(0x8CEFEFEF) : Color(0x60191919)),
//             ),
//             filled: true,
//             fillColor: Colors.transparent,
//             contentPadding: const EdgeInsets.symmetric(
//               vertical: 14,
//               horizontal: 12,
//             ),
//             enabledBorder: OutlineInputBorder(
//               borderRadius: BorderRadius.circular(12),
//               borderSide: BorderSide(
//                 color: errorText != null
//                     ? Colors.red
//                     : (widget.darkMode ? Color(0x80EFEFEF) : Color(0x80191919)),
//               ),
//             ),
//             focusedBorder: OutlineInputBorder(
//               borderRadius: BorderRadius.circular(12),
//               borderSide: BorderSide(
//                 color: errorText != null
//                     ? Colors.red
//                     : (widget.darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919)),
//               ),
//             ),
//           ),
//           style: TextStyle(
//             color: widget.darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
//             fontFamily: 'Hyperion',
//             fontWeight: FontWeight.w700,
//             fontSize: 15,
//           ),
//           validator: widget.required
//               ? (value) {
//                   if (value == null || value.isEmpty) {
//                     setState(() {
//                       errorText = 'required';
//                     });
//                     return '';
//                   }
//                   setState(() {
//                     errorText = null;
//                   });
//                   return null;
//                 }
//               : null,
//         ),
//       ],
//     );
//   }
// }

// /// =======================
// ///     PASSWORD FIELD
// /// =======================

// Widget buildPasswordField(
//   bool darkMode,
//   String label, {
//   String? labelNote,
//   required bool obscureText,
//   required VoidCallback toggle,
//   TextEditingController? controller,
// }) {
//   return _PasswordFieldWithInternalError(
//     darkMode: darkMode,
//     label: label,
//     labelNote: labelNote,
//     obscureText: obscureText,
//     toggle: toggle,
//     controller: controller,
//   );
// }

// class _PasswordFieldWithInternalError extends StatefulWidget {
//   final bool darkMode;
//   final String label;
//   final String? labelNote;
//   final bool obscureText;
//   final VoidCallback toggle;
//   final TextEditingController? controller;

//   const _PasswordFieldWithInternalError({
//     required this.darkMode,
//     required this.label,
//     this.labelNote,
//     required this.obscureText,
//     required this.toggle,
//     this.controller,
//   });

//   @override
//   State<_PasswordFieldWithInternalError> createState() =>
//       _PasswordFieldWithInternalErrorState();
// }

// class _PasswordFieldWithInternalErrorState
//     extends State<_PasswordFieldWithInternalError> {
//   String? errorText;

//   @override
//   Widget build(BuildContext context) {
//     return Column(
//       crossAxisAlignment: CrossAxisAlignment.start,
//       children: [
//         Row(
//           crossAxisAlignment: CrossAxisAlignment.end,
//           children: [
//             Text(
//               widget.label,
//               style: TextStyle(
//                 color: widget.darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
//                 fontFamily: 'Hyperion',
//                 fontWeight: FontWeight.w700,
//                 fontSize: 15,
//               ),
//             ),
//             if (widget.labelNote != null) ...[
//               const SizedBox(width: 6),
//               Text(
//                 widget.labelNote!,
//                 style: TextStyle(
//                   fontFamily: 'Hyperion',
//                   fontWeight: FontWeight.w700,
//                   fontSize: 8,
//                   color: widget.darkMode
//                       ? const Color(0x80EFEFEF)
//                       : const Color(0xFF191919),
//                 ),
//               ),
//             ],
//           ],
//         ),
//         const SizedBox(height: 6),
//         TextFormField(
//           controller: widget.controller,
//           obscureText: widget.obscureText,
//           decoration: InputDecoration(
//             hintText: errorText ?? '••••••••',
//             hintStyle: TextStyle(
//               fontFamily: 'Hyperion',
//               fontWeight: FontWeight.w700,
//               color: errorText != null
//                   ? Colors.red
//                   : (widget.darkMode ? Color(0x61EFEFEF) : Color(0x61191919)),
//             ),
//             suffixIcon: IconButton(
//               onPressed: widget.toggle,
//               icon: Image.asset(
//                 'assets/images/obscure_icon.png',
//                 height: 30,
//                 width: 30,
//                 color: widget.darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
//               ),
//             ),
//             enabledBorder: OutlineInputBorder(
//               borderRadius: BorderRadius.circular(12),
//               borderSide: BorderSide(
//                 color: errorText != null
//                     ? Colors.red
//                     : (widget.darkMode ? Color(0x80EFEFEF) : Color(0x80191919)),
//               ),
//             ),
//             focusedBorder: OutlineInputBorder(
//               borderRadius: BorderRadius.circular(12),
//               borderSide: BorderSide(
//                 color: errorText != null
//                     ? Colors.red
//                     : (widget.darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919)),
//               ),
//             ),
//             contentPadding: const EdgeInsets.symmetric(
//               vertical: 14,
//               horizontal: 12,
//             ),
//           ),
//           style: TextStyle(
//             color: widget.darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
//             fontFamily: 'Hyperion',
//             fontWeight: FontWeight.w700,
//             fontSize: 15,
//           ),
//           validator: (value) {
//             if (value == null || value.isEmpty) {
//               setState(() {
//                 errorText = 'required';
//               });
//               return '';
//             }
//             setState(() {
//               errorText = null;
//             });
//             return null;
//           },
//         ),
//       ],
//     );
//   }
// }

// /// =======================
// ///     ICON BUTTON BUILDER
// /// =======================

// Widget buildIconButton(bool darkMode, String assetPath) {
//   return GestureDetector(
//     onTap: () {},
//     child: Container(
//       height: 50,
//       width: 50,
//       decoration: BoxDecoration(
//         color: darkMode ? Colors.white : Colors.black,
//         borderRadius: BorderRadius.circular(12),
//         boxShadow: [
//           BoxShadow(
//             color: darkMode ? Colors.black12 : Colors.white12,
//             blurRadius: 4,
//             offset: Offset(0, 2),
//           ),
//         ],
//       ),
//       padding: const EdgeInsets.all(10),
//       child: Image.asset(
//         assetPath,
//         fit: BoxFit.contain,
//         color: darkMode ? Colors.black : Colors.white,
//       ),
//     ),
//   );
// }

// /// =======================
// ///     DROPDOWN FIELDS
// /// =======================

// Widget buildDropdownField(
//   bool darkMode,
//   String label,
//   List<String> items,
//   String? selectedValue,
//   void Function(String?) onChanged, {
//   String? labelNote,
//   bool required = false,
// }) {
//   final hasError = required && (selectedValue == null || selectedValue.isEmpty);

//   return Column(
//     crossAxisAlignment: CrossAxisAlignment.start,
//     children: [
//       Row(
//         crossAxisAlignment: CrossAxisAlignment.end,
//         children: [
//           Text(
//             label,
//             style: TextStyle(
//               fontFamily: 'Hyperion',
//               fontSize: 15,
//               fontWeight: FontWeight.w700,
//               color: darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
//             ),
//           ),
//           if (labelNote != null) ...[
//             const SizedBox(width: 6),
//             Text(
//               labelNote,
//               style: TextStyle(
//                 fontFamily: 'Hyperion',
//                 fontSize: 8,
//                 fontWeight: FontWeight.w700,
//                 color: darkMode ? Color(0x80EFEFEF) : Color(0xFF191919),
//               ),
//             ),
//           ],
//         ],
//       ),
//       const SizedBox(height: 6),
//       DropdownButtonFormField<String>(
//         value: selectedValue,
//         onChanged: onChanged,
//         items: items
//             .map((item) => DropdownMenuItem(value: item, child: Text(item)))
//             .toList(),
//         decoration: InputDecoration(
//           filled: true,
//           fillColor: Colors.transparent,
//           contentPadding: const EdgeInsets.symmetric(
//             vertical: 14,
//             horizontal: 12,
//           ),
//           enabledBorder: OutlineInputBorder(
//             borderRadius: BorderRadius.circular(12),
//             borderSide: BorderSide(
//               color: hasError
//                   ? Colors.red
//                   : (darkMode ? Color(0x80EFEFEF) : Color(0x80191919)),
//             ),
//           ),
//           focusedBorder: OutlineInputBorder(
//             borderRadius: BorderRadius.circular(12),
//             borderSide: BorderSide(
//               color: hasError
//                   ? Colors.red
//                   : (darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919)),
//             ),
//           ),
//         ),
//         style: TextStyle(
//           fontFamily: 'Hyperion',
//           fontWeight: FontWeight.w700,
//           fontSize: 15,
//           color: darkMode ? Color(0xFFEFEFEF) : Color(0xFF191919),
//         ),
//         validator: required
//             ? (value) {
//                 if (value == null || value.isEmpty) {
//                   return '';
//                 }
//                 return null;
//               }
//             : null,
//       ),
//     ],
//   );
// }

// /// =======================
// ///     PROFILE PICKER
// /// =======================

// Widget buildProfileImageSelector({
//   required bool darkMode,
//   required VoidCallback onTap,
//   required String? imagePath,
// }) {
//   return GestureDetector(
//     onTap: onTap,
//     child: CircleAvatar(
//       radius: 50,
//       backgroundColor: darkMode ? Colors.white10 : Colors.black12,
//       backgroundImage: imagePath != null ? FileImage(File(imagePath)) : null,
//       child: imagePath == null
//           ? Icon(
//               Icons.add_a_photo,
//               size: 30,
//               color: darkMode ? Colors.white : Colors.black,
//             )
//           : null,
//     ),
//   );
// }

// /// =======================
// ///     DROPDOWN LISTS
// /// =======================

// const List<String> countryList = [
//   "Afghanistan",
//   "Albania",
//   "Algeria",
//   "Andorra",
//   "Angola",
//   "Argentina",
//   "Armenia",
//   "Australia",
//   "Austria",
//   "Azerbaijan",
//   "Bahamas",
//   "Bahrain",
//   "Bangladesh",
//   "Barbados",
//   "Belarus",
//   "Belgium",
//   "Belize",
//   "Benin",
//   "Bhutan",
//   "Bolivia",
//   "Bosnia and Herzegovina",
//   "Botswana",
//   "Brazil",
//   "Brunei",
//   "Bulgaria",
//   "Burkina Faso",
//   "Burundi",
//   "Cabo Verde",
//   "Cambodia",
//   "Cameroon",
//   "Canada",
//   "Chad",
//   "Chile",
//   "China",
//   "Colombia",
//   "Comoros",
//   "Congo",
//   "Costa Rica",
//   "Croatia",
//   "Cuba",
//   "Cyprus",
//   "Czech Republic",
//   "Denmark",
//   "Djibouti",
//   "Dominica",
//   "Dominican Republic",
//   "Ecuador",
//   "Egypt",
//   "El Salvador",
//   "Equatorial Guinea",
//   "Eritrea",
//   "Estonia",
//   "Eswatini",
//   "Ethiopia",
//   "Fiji",
//   "Finland",
//   "France",
//   "Gabon",
//   "Gambia",
//   "Georgia",
//   "Germany",
//   "Ghana",
//   "Greece",
//   "Grenada",
//   "Guatemala",
//   "Guinea",
//   "Guyana",
//   "Haiti",
//   "Honduras",
//   "Hungary",
//   "Iceland",
//   "India",
//   "Indonesia",
//   "Iran",
//   "Iraq",
//   "Ireland",
//   "Italy",
//   "Jamaica",
//   "Japan",
//   "Jordan",
//   "Kazakhstan",
//   "Kenya",
//   "Kuwait",
//   "Kyrgyzstan",
//   "Laos",
//   "Latvia",
//   "Lebanon",
//   "Lesotho",
//   "Liberia",
//   "Libya",
//   "Liechtenstein",
//   "Lithuania",
//   "Luxembourg",
//   "Madagascar",
//   "Malawi",
//   "Malaysia",
//   "Maldives",
//   "Mali",
//   "Malta",
//   "Mauritania",
//   "Mauritius",
//   "Mexico",
//   "Moldova",
//   "Monaco",
//   "Mongolia",
//   "Montenegro",
//   "Morocco",
//   "Mozambique",
//   "Myanmar",
//   "Namibia",
//   "Nepal",
//   "Netherlands",
//   "New Zealand",
//   "Nicaragua",
//   "Niger",
//   "Nigeria",
//   "North Korea",
//   "North Macedonia",
//   "Norway",
//   "Oman",
//   "Pakistan",
//   "Palau",
//   "Palestine",
//   "Panama",
//   "Paraguay",
//   "Peru",
//   "Philippines",
//   "Poland",
//   "Portugal",
//   "Qatar",
//   "Romania",
//   "Russia",
//   "Rwanda",
//   "Saint Kitts and Nevis",
//   "Saint Lucia",
//   "Saint Vincent",
//   "Samoa",
//   "San Marino",
//   "Saudi Arabia",
//   "Senegal",
//   "Serbia",
//   "Seychelles",
//   "Sierra Leone",
//   "Singapore",
//   "Slovakia",
//   "Slovenia",
//   "Solomon Islands",
//   "Somalia",
//   "South Africa",
//   "South Korea",
//   "South Sudan",
//   "Spain",
//   "Sri Lanka",
//   "Sudan",
//   "Suriname",
//   "Sweden",
//   "Switzerland",
//   "Syria",
//   "Taiwan",
//   "Tajikistan",
//   "Tanzania",
//   "Thailand",
//   "Togo",
//   "Tonga",
//   "Trinidad and Tobago",
//   "Tunisia",
//   "Turkey",
//   "Turkmenistan",
//   "Uganda",
//   "Ukraine",
//   "United Arab Emirates",
//   "United Kingdom",
//   "United States",
//   "Uruguay",
//   "Uzbekistan",
//   "Vanuatu",
//   "Venezuela",
//   "Vietnam",
//   "Yemen",
//   "Zambia",
//   "Zimbabwe",
// ];

// final List<String> timeZoneList = [
//   'UTC−12:00',
//   'UTC−11:00',
//   'UTC−10:00',
//   'UTC−09:00',
//   'UTC−08:00',
//   'UTC−07:00',
//   'UTC−06:00',
//   'UTC−05:00',
//   'UTC−04:00',
//   'UTC−03:00',
//   'UTC−02:00',
//   'UTC−01:00',
//   'UTC±00:00',
//   'UTC+01:00',
//   'UTC+02:00',
//   'UTC+03:00',
//   'UTC+04:00',
//   'UTC+05:00',
//   'UTC+06:00',
//   'UTC+07:00',
//   'UTC+08:00',
//   'UTC+09:00',
//   'UTC+10:00',
//   'UTC+11:00',
//   'UTC+12:00',
//   'UTC+13:00',
//   'UTC+14:00',
// ];

// final List<String> titleList = [
//   'Mr.',
//   'Mrs.',
//   'Ms.',
//   'Miss',
//   'Dr.',
//   'Prof.',
//   'Eng.',
// ];

// final List<String> genderList = ['Male', 'Female'];
