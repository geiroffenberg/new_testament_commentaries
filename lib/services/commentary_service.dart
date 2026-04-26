import 'dart:async';
import 'dart:convert';

import 'package:flutter/services.dart';

import '../models/commentary_source.dart';
import '../models/verse.dart';

abstract class CommentaryService {
  Future<String?> getCommentary(CommentarySource source, Verse verse);
}

class JsonCommentaryService implements CommentaryService {
  static final JsonCommentaryService _instance = JsonCommentaryService._internal();

  final Map<String, Map<String, dynamic>> _cache = {};

  JsonCommentaryService._internal();

  factory JsonCommentaryService() {
    return _instance;
  }

  String _getSourceId(CommentarySource source) {
    switch (source) {
      case CommentarySource.clarke:
        return 'clarke';
      case CommentarySource.jfb:
        return 'jfb';
      case CommentarySource.rwp:
        return 'rwp';
      case CommentarySource.mhcc:
        return 'mhcc';
    }
  }

  @override
  Future<String?> getCommentary(CommentarySource source, Verse verse) async {
    final sourceId = _getSourceId(source);
    final cacheKey = '$sourceId/${verse.bookName}/${verse.chapter}';

    // Return cached data if available
    if (_cache.containsKey(cacheKey)) {
      final chapterData = _cache[cacheKey];
      return chapterData?['verses']?[verse.verse.toString()];
    }

    try {
      // Load JSON file for this chapter
      final assetPath =
          'assets/commentaries_json/$sourceId/${verse.bookName}/${verse.chapter}.json';
      final jsonString = await rootBundle.loadString(assetPath);
      final chapterData = json.decode(jsonString) as Map<String, dynamic>;

      // Cache for future use
      _cache[cacheKey] = chapterData;

      // Return the specific verse commentary
      return chapterData['verses']?[verse.verse.toString()];
    } catch (e) {
      // File not found or parsing error - return null (no commentary for this verse)
      return null;
    }
  }
}

class MockCommentaryService implements CommentaryService {
  static const Map<String, String> _clarke = {
    'Matthew 5:3':
        'Blessed are the poor in spirit: This points to deep humility before God, the true doorway into the kingdom.',
    'John 1:1':
        'The Word was in the beginning, distinct in person and fully divine in essence.',
  };

  static const Map<String, String> _jfb = {
    'Matthew 5:3':
        'The first beatitude marks those who know their need and therefore are ready for grace.',
    'John 1:1':
        'The pre-existence of the Word is affirmed, and His relation with God is both personal and eternal.',
  };

  static const Map<String, String> _rwp = {
    'John 1:1':
        'Imperfect tense of eimi suggests continuous existence: the Word already was when the beginning came to be.',
    'Romans 8:1':
        'No condemnation stands for those in Christ Jesus, because their standing is now defined by union with Him.',
  };

  static const Map<String, String> _mhcc = {
    'Matthew 5:3':
        'Those who are lowly in their own eyes are blessed, for they gladly receive God\'s mercy.',
    'Romans 8:1':
        'Believers are delivered from guilt and fear of wrath through Christ.',
  };

  @override
  Future<String?> getCommentary(CommentarySource source, Verse verse) async {
    // Small delay to mimic real I/O and exercise loading states in the UI.
    await Future<void>.delayed(const Duration(milliseconds: 180));

    final key = verse.reference;
    final map = switch (source) {
      CommentarySource.clarke => _clarke,
      CommentarySource.jfb => _jfb,
      CommentarySource.rwp => _rwp,
      CommentarySource.mhcc => _mhcc,
    };

    return map[key];
  }
}
