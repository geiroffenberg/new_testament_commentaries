enum CommentarySource { clarke, jfb, rwp, mhcc }

extension CommentarySourceUi on CommentarySource {
  String get shortLabel {
    switch (this) {
      case CommentarySource.clarke:
        return 'Clarke';
      case CommentarySource.jfb:
        return 'JFB';
      case CommentarySource.rwp:
        return 'RWP';
      case CommentarySource.mhcc:
        return 'MHCC';
    }
  }

  String get fullTitle {
    switch (this) {
      case CommentarySource.clarke:
        return 'Adam Clarke';
      case CommentarySource.jfb:
        return 'Jamieson-Fausset-Brown';
      case CommentarySource.rwp:
        return 'Robertson Word Pictures';
      case CommentarySource.mhcc:
        return 'Matthew Henry Concise';
    }
  }
}
