import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';

import 'screens/bible_reader.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // google_mobile_ads is not implemented for Flutter web.
  if (!kIsWeb) {
    await MobileAds.instance.initialize();
  }
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NT Commentaries',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        textTheme: GoogleFonts.ubuntuTextTheme(),
        primaryTextTheme: GoogleFonts.ubuntuTextTheme(),
        useMaterial3: true,
      ),
      home: const BibleReader(),
    );
  }
}
