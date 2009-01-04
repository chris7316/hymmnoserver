# -*- encoding: utf-8 -*-

import _mysql
db = _mysql.connect("localhost", "aurica", "misha", "hymmnoserver")

while True:
	print "Word to be added: "
	word = "'%s'" % raw_input().replace("'", "\\'")
	print "English translation: "
	english = "'%s'" % raw_input().replace("'", "\\'")
	print "Japanese form: "
	japanese = "'%s'" % raw_input().replace("'", "\\'")
	print "Kana form: "
	kana = "'%s'" % raw_input().replace("'", "\\'")
	print "Romaji form: "
	romaji = "'%s'" % raw_input().replace("'", "\\'")
	print "1) 中央正純律（共通語)"
	print "2) クルトシエール律（Ⅰ紀前古代語）"
	print "3) クラスタ律（クラスタ地方語）"
	print "4) アルファ律（オリジンスペル）"
	print "5) 古メタファルス律（Ⅰ紀神聖語）"
	print "6) 新約パスタリエ（パスタリア成語）"
	print "7) アルファ律（オリジンスペル：EOLIA属）"
	print "Which school? "
	school = int(raw_input())
	print "1) Emotion verb"
	print "2) verb"
	print "3) adverb"
	print "4) noun"
	print "5) conjunction"
	print "6) preposition"
	print "7) Emotion sound (II)"
	print "8) adjective"
	print "9) verb/noun"
	print "10) adjective/noun"
	print "11) verb/adjective"
	print "12) particle"
	print "13) Emotion sound (III)"
	print "14) Emotion sound (I)"
	print "15) pronoun"
	print "16) interjection"
	print "17) Emotion sound (II)/adjective"
	print "18) conjunction/verb"
	print "19) noun/adverb"
	print "20) adjective/adverb"
	print "Syntax class: "
	syntax = int(raw_input())
	print "Comments: "
	comments = "'%s'" % raw_input().replace("'", "\\'")
	if comments == "''":
		comments = "NULL"
		
	db.query("insert into hymmnos values (%s, %s, %s, %i, %s, %s, %s, %i)" % \
	 (word, english, japanese, school, kana, romaji, comments, syntax))
	print
	