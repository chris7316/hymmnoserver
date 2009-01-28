<?php
	#Set up constants required for processing.
	$EMOTION_VOWELS = 'A|I|U|E|O|N|YA|YI|YU|YE|YO|YN|LYA|LYI|LYU|LYE|LYO|LYN';
	$EMOTION_VOWELS_REGEXP = '('.$EMOTION_VOWELS.')';
	$EMOTION_VOWELS_REGEXP_FULL = '('.$EMOTION_VOWELS.'|\.)?';
	$PARTICLES = array(12, 16, 18, 21);
	$VERBS = array(2, 9, 11, 21);
	$ADVERBS = array(3, 19, 20);
	$NOUNS = array(4, 9, 10, 15, 19);
	$ADJECTIVES = array(8, 10, 11, 17, 20, 7);
	$PREPOSITIONS = array(6);
	
	#Define state variables.
	$valid = true;
	$reason = NULL;
	$generation = 0;
	
	#Read all Emotion Verbs from the database.
	$emotion_verbs = array();
	$stmt = $mysql->prepare("SELECT word FROM hymmnos WHERE class = 1");
	$stmt->execute();
	$stmt->store_result();
	$stmt->bind_result($word);
	while($stmt->fetch()){
		#Store the Emotion Verb, the number of Emotion Vowels, and a regexp version.
		array_push($emotion_verbs, array('/^'.str_replace('.', $EMOTION_VOWELS_REGEXP_FULL, $word).'(eh)?$/', substr_count($word, '.'), $word));
	}
	$stmt->free_result();
	$stmt->close();
	
	#Read the definition of every provided word and construct the displayable Hymmnos string.
	$word_list = array();
	for($i = 0; $i < count($words); $i++){
		$word = readWord($words[$i]);
		$words[$i] = $word;
		array_push($word_list, decorateWord($word[0], $word[3], $word[5], false));
	}
	$word_string = implode(" ", $word_list);
	$word_list = NULL;
	
	#Read a word from the database; Emotion Verbs and Emotion Vowel-prefixed words are detected.
	function readWord($word){
		$emotion_verb = processEmotionVerb($word);
		if($emotion_verb != NULL){
			return $emotion_verb;
		}
		$emotion_word = processEmotionWord($word);
		if($emotion_word != NULL){
			return $emotion_word;
		}
		return queryWord($word);
	}
	
	#Read a word from the database.
	#Return format: [word, english, kana, class, dialect, decorations]
	function queryWord($word){
		$result = NULL;
		
		global $mysql;
		$stmt = $mysql->prepare("SELECT word, meaning_english, kana, class, school FROM hymmnos WHERE word = ? ORDER BY school ASC LIMIT 1");
		$stmt->bind_param("s", $word);
		$stmt->execute();
		$stmt->store_result();
		if($stmt->num_rows > 0){
			$stmt->bind_result($r_word, $english, $kana, $class, $dialect);
			$stmt->fetch();
			$result = array($r_word, $english, $kana, $class, $dialect, NULL);
		}else{
			$result = array($word, NULL, NULL, 0, 0, NULL);
		}
		$stmt->free_result();
		$stmt->close();
		
		return $result;
	}
	
	#Determine whether a word is an Emotion Verb; if so, read it from the database.
	#Return format: [word, english, kana, class, dialect, decorations] | NULL
	function processEmotionVerb($word){
		global $emotion_verbs;
		
		foreach($emotion_verbs as $emotion_verb){
			if(preg_match($emotion_verb[0], $word, $matches)){#Match found.
				$d_word = queryWord($emotion_verb[2]);
				if($d_word[3] > 0){#Match found.
					if(count($matches) - 1 <= $emotion_verb[1]){#Work around a permanent PHP bug.
						for($i = $emotion_verb[1] - count($matches); $i > -1; $i--){
							array_push($matches, '.');
						}
						array_push($matches, ''); 
					}
					$decorations = array();
					foreach(array_slice($matches, 1, -1) as $decoration){
						if($decoration == NULL){
							array_push($decorations, '.');
						}else{
							array_push($decorations, $decoration);
						}
					}
					array_push($decorations, $matches[count($matches) - 1]);
					$d_word[5] = $decorations;
					return $d_word;
				}
			}
		}
		return NULL;
	}
	
	#Determine whether a word is an Emotion Vowel-prefixed word; if so, read it from the database.
	#Return format: [word, english, kana, class, dialect, decorations] | NULL
	function processEmotionWord($word){
		global $EMOTION_VOWELS_REGEXP;
		
		if(preg_match("/^$EMOTION_VOWELS_REGEXP(.+)$/", $word, $matches)){
			$d_word = queryWord($matches[2]);
			if($d_word[3] > 0){#Match found.
				$d_word[5] = array($matches[1]);
				return $d_word;
			}
		}
		return NULL;
	}
	
	#Insert Emotion Vowels or blanks into Emotion Verbs or prefix other words.
	function decorateWord($word, $class, $decorations, $colour){
		if($decorations == NULL){
			return $word;
		}
		
		if($class == 1){#Emotion Verb
			$result = '';
			$chunks = split('\.', $word);
			$i = 0;
			foreach(array_slice($decorations, 0, -1) as $vowel){
				$result = $result.$chunks[$i];
				if($colour){
					$result = $result."<span style=\"color: yellow;\">".$vowel."</span>";
				}else{
					$result = $result.$vowel;
				}
				$i++;
			}
			if($colour){
				return $result."<span style=\"color: magenta;\">".$decorations[count($decorations) - 1]."</span>";
			}else{
				return $result.$decorations[count($decorations) - 1];
			}
		}
		
		global $NOUNS;
		global $ADJECTIVES;
		if(in_array($class, $NOUNS) || in_array($class, $ADJECTIVES)){#noun/adj
			if($colour){
				return "<span style=\"color: yellow;\">".$decorations[0]."</span>".$word;
			}else{
				return $decorations[0].$word;
			}
		}
	}
	
	#Renders a collection of words in the output table.
	function renderSection($header, $colour, $words){
		echo '<tr>';
			echo "<td style=\"width: 75px; background: $colour; color: white; font-size: 0.6em; text-align: center;\">$header</td>";
			echo '<td style="width: 555px; background: grey; padding: 0;"><table style="width: 100%; color: white; font-size: 0.8em;">';
				foreach($words as $word){
					renderWord($word);
				}
			echo '</table></td>';
		echo '</tr>';
	}
	
	#Renders a single word in a section in the output table.
	function renderWord($word){
		global $SYNTAX_CLASS;
		
		list($l_word, $english, $kana, $class, $dialect, $decorations) = $word;
		$base_word = htmlspecialchars($l_word);
		if($class == 0){
			$english = '???';
			$kana = '???';
		}else{
			if($decorations != NULL){
				$l_word = htmlspecialchars(decorateWord($l_word, $class, $decorations, true));
			}
			$l_word = "<a href=\"javascript:popUpWord('$base_word', $dialect)\" style=\"color: white;\">".$l_word."</a>";
		}
		
		echo "<tr>";
			echo "<td class=\"word-header-$class\" style=\"width: 80px;\">$l_word</td>";
			echo "<td class=\"word-header-$class\" style=\"width: 75px;\">$SYNTAX_CLASS[$class]</td>";
			echo "<td class=\"word-header-$class\" style=\"width: 275px;\">$english</td>";
			echo "<td class=\"word-header-$class\" style=\"width: 100px;\">$kana</td>";
		echo "</tr>";
	}
	
	#Processes a list of words, attempting to determine which sublists belong to which components of the sentence.
	#The output is rendered as it is determined. (This is a linear evaluation)
	function evaluateWords($words){
		global $generation;
		global $valid;
		global $reason;
		
		$emotionless_subject = false;
		
		#Check for Emotion words.
		list($remainder, $processed) = captureEmotionSound($words);
		if($valid){
			if($remainder == $words){#See if it's a Pastalia sentence.
				list($remainder, $processed) = captureEmotionVerb($remainder);
				if($remainder == $words){#No Emotion Verb, so this must be gen 1.
					$generation = 1;
					list($remainder, $processed) = captureSubject($remainder, true);
					if($remainder != $words){#The first object is this sentence's subject.
						$emotionless_subject = true;
					}else{#Hacks are fun. The subject-catcher will need to be more flexible in v2.
						$valid = true;
					}
				}
			}
			
			if($valid){
				if($generation == 1){#Make sure there's a verb.
					list($remainder, $processed) = popParticles($remainder);
					list($remainder, $processed) = captureVerbPhrase($remainder, true, false);
				}
				
				if($valid){#Check for subject changes.
					if($generation == 1 && !$emotionless_subject){#optional.
						list($rest, $processed) = captureSubject($remainder, false);
						if($valid){
							if($rest != $remainder){#A verb is required.
								list($rest, $processed) = captureVerbPhrase($rest, true, false);
							}
							$remainder = $rest;
						}
					}elseif($generation == 2 && $words[0][0] == 'x.'){#required.
						list($remainder, $processed) = captureSubject($remainder, true);
						if($valid){#An Emotion Verb is required.
							list($rest, $processed) = captureEmotionVerb($remainder);
							if($rest == $remainder){#Not found.
								$valid = false;
								$reason = "expected Emotion Verb";
							}
							$remainder = $rest;
						}
					}
					
					if($valid){#Evaluate the rest of the sentence.
						#An object is allowed before a compound.
						list($rest, $processed, $is_oo) = captureNounPhrase($remainder, false, false);
						if($valid && !$is_oo){#If OO is encountered, the sentence is done.
							if($remainder == $rest && $generation == 2){#Gen 2 allows EV to stand in for O.
								list($rest, $processed) = captureEmotionVerbPhrase($rest, false, false);
							}
							if($valid){
								list($remainder, $processed) = captureCompound($rest);
							}
						}else{
							$remainder = $rest;
						}
					}
				}
			}
		}
		
		if(count($remainder) > 0){
			if($valid){
				$valid = false;
				$reason = "unexpected words at end of sentence";
			}
			renderSection("Not evaluated", "black", $remainder);
		}
	}
	
	#Attempts to find an Emotion Sound at the start of the word list.
	#Return: [remaining words, consumed words]
	function captureEmotionSound($words){
		if(count($words) < 3){
			return array($words, array());
		}
		global $valid;
		global $reason;
		global $generation;
		
		if($words[0][3] == 14){
			if($generation == 2){
				$valid = false;
				$reason = "Emotion Sounds cannot be used with Emotion Verbs";
				return array($words, array());
			}
			if($words[1][3] == 7 || $words[1][3] == 17){
				if($words[2][3] == 13){
					$generation = 1;
					$processed = array_slice($words, 0, 3);
					renderSection("Emotion Sound", "#004400", $processed);
					return array(array_slice($words, 3), $processed);
				}else{
					$valid = false;
					$reason = "missing Emotion Sound (III)";
				}
			}else{
				$valid = false;
				$reason = "missing Emotion Sound (II)";
			}
		}
		return array($words, array());
	}
	
	#Attempts to find an Emotion Verb at the start of the word list.
	#Return: [remaining words, consumed words]
	function captureEmotionVerb($words){
		if(count($words) < 1){
			return array($words, array());
		}
		global $valid;
		global $reason;
		global $generation;
		
		if($words[0][3] == 1){
			$generation = 2;
			$processed = array_slice($words, 0, 1);
			renderSection("Emotion Verb", "#004400", $processed);
			return array(array_slice($words, 1), $processed);
		}
		return array($words, array());
	}
	
	#Attempts to strip particles between phrases.
	#Return: [remaining words, consumed words]
	function popParticles($words){#Gets rid of classes that really mess things up.
		global $PARTICLES;
		
		$i = 0;
		while(true){
			$word = $words[$i];
			if($word == NULL){
				break;
			}
			$class = $word[3];
			if(!(in_array($class, $PARTICLES))){
				break;
			}
			$i++;
		}
		if($i > 0){
			$processed = array_slice($words, 0, $i);
			renderSection("", "#222222", $processed);
			return array(array_slice($words, $i), $processed);
		}
		return array($words, array());
	}
	
	#Attempts to find a subject at the start of the word list.
	#required: true if its absence means the sentence is invalid
	#Return: [remaining words, consumed words]
	function captureSubject($words, $required){
		if(count($words) < 1){
			return array($words, array());
		}
		global $valid;
		global $reason;
		global $generation;
		
		$rre_component = NULL;
		$processed = NULL;
		if($words[0][0] == 'rre'){
			$rre_component = array_slice($words, 0, 1);
			$words = array_slice($words, 1);
			$required = true;
		}else{
			$rre_component = array();
			$processed = array();
		}
		if($required){
			list($words, $processed, $is_oo) = captureNounPhrase($words, $required, true);
			if($valid){
				$processed = array_merge($rre_component, $processed);
				renderSection("subject", "#000033", $processed);
			}else{
				$words = array_merge($rre_component, $words);
			}
		}
		return array($words, $processed);
	}
	
	#Attempts to find a Noun Phrase at the start of the word list.
	#required: true if its absence means the sentence is invalid
	#nest: true if this function is not responsible for rendering its results
	#suppress_oo: true if [OO] is not permitted here, meaning that structures must be possessive, not sequential
	#Return: [remaining words, consumed words, whether the NP might contain two NPs]
	function captureNounPhrase($words, $required, $nest, $suppress_oo=false){#Last part of return indicates whether this is OO.
		global $NOUNS;
		global $ADJECTIVES;
		global $PARTICLES;
		global $PREPOSITIONS;
		global $valid;
		global $reason;
		global $generation;
		
		$np_valid = false;
		$preposition_hit = false;
		$oo_possible = false;
		$end_reached = false;
		$i = 0;
		while(true){
			$word = $words[$i];
			if($word == NULL){
				$end_reached = true;
				break;
			}
			$class = $word[3];
			if($np_valid){#Post-noun.
				if($class == 5){#Conjunction.
					list($conj_remainder, $conj_processed, $is_oo) = captureNounPhrase(array_slice($words, $i + 1), true, true);
					if($valid){
						$i += count($conj_processed) + 1; #Account for the conjunction.
						$oo_possible = true;
					}else{
						$np_valid = false;
						$reason = "conjunction encountered, but noun phrase not found";
						break;
					}
				}elseif(in_array($class, $PREPOSITIONS)){
					$preposition_hit = true;
				}elseif(in_array($class, $NOUNS)){
					if($preposition_hit){
						$i--; #Assume the preposition belongs to the following NP.
						break;
					}else{#Assume possessive, but allow for the possibility of two NPs.
						$oo_possible = true;
					}
				}else{#NP complete.
					break;
				}
			}else{
				if(in_array($class, $NOUNS)){
					$np_valid = true;
				}elseif(!((in_array($class, $ADJECTIVES)) || in_array($class, $PARTICLES))){#NP not complete.
					if($required){
						$valid = false;
						$reason = "noun phrase expected";
					}
					break;
				}
			}
			$i++;
		}
		if($np_valid){
			$processed = array_slice($words, 0, $i);
			if($oo_possible && $end_reached && !$suppress_oo){
				if(!$nest){
					renderSection("object<br/>object", "#000044", $processed);
				}
			}else{
				if(!$nest){
					renderSection("object", "#000044", $processed);
				}
			}
			return array(array_slice($words, $i), $processed, $oo_possible && $end_reached);
		}
		return array($words, array(), false);
	}
	
	#Attempts to find a Verb Phrase at the start of the word list.
	#required: true if its absence means the sentence is invalid
	#nest: true if this function is not responsible for rendering its results
	#Return: [remaining words, consumed words]
	function captureVerbPhrase($words, $required, $nest){
		global $VERBS;
		global $ADVERBS;
		global $PARTICLES;
		global $valid;
		global $reason;
		global $generation;
		
		$vp_valid = false;
		$i = 0;
		while(true){
			$word = $words[$i];
			if($word == NULL){
				break;
			}
			$class = $word[3];
			if($vp_valid){#Post-verb.
				if($class == 5){#Conjunction.
					list($conj_remainder, $conj_processed) = captureVerbPhrase(array_slice($words, $i + 1), true, true);
					if($valid){
						$i += count($conj_processed) + 1; #Account for the conjunction.
					}else{
						$vp_valid = false;
						$reason = "conjunction encountered, but verb phrase not found";
						break;
					}
				}elseif(!(in_array($class, $ADVERBS))){#VP complete.
					break;
				}else{#Rule out object hits on 19 and 20.
					if($class == 19 || $class == 20){
						break;
					}
				}
			}else{
				if(in_array($class, $VERBS) || ($generation == 2 && $class == 1)){
					$vp_valid = true;
				}elseif(!((in_array($class, $ADVERBS)) || in_array($class, $PARTICLES))){#VP not complete.
					if($required){
						$valid = false;
						$reason = "verb phrase expected";
					}
					break;
				}
			}
			$i++;
		}
		if($vp_valid){
			$processed = array_slice($words, 0, $i);
			if(!$nest){
				renderSection("verb", "#440000", $processed);
			}
			return array(array_slice($words, $i), $processed);
		}
		return array($words, array());
	}
	
	#Attempts to find an Emotion Verb Phrase at the start of the word list.
	#required: true if its absence means the sentence is invalid
	#nest: true if this function is not responsible for rendering its results
	#Return: [remaining words, consumed words]
	function captureEmotionVerbPhrase($words, $required, $nest){
		global $ADVERBS;
		global $PARTICLES;
		global $valid;
		global $reason;
		global $generation;
		
		$evp_valid = false;
		$i = 0;
		while(true){
			$word = $words[$i];
			if($word == NULL){
				break;
			}
			$class = $word[3];
			if($evp_valid){#Post-verb.
				if(!(in_array($class, $ADVERBS))){#EVP complete.
					break;
				}else{#Rule out object hits on 19 and 20.
					if($class == 19 || $class == 20){
						break;
					}
				}
			}else{
				if($class == 1){
					foreach($word[5] as $modifier){
						if($modifier != '.' && $modifier != ''){
							if($required){
								$valid = false;
								$reason = "Emotion Verb phrase excpected";
							}
							return array($words, array());
						}
					}
					$evp_valid = true;
				}elseif(!((in_array($class, $ADVERBS)) || in_array($class, $PARTICLES))){#VP not complete.
					if($required){
						$valid = false;
						$reason = "Emotion Verb phrase expected";
					}
					break;
				}
			}
			$i++;
		}
		if($evp_valid){
			$processed = array_slice($words, 0, $i);
			if(!$nest){
				renderSection("action", "#220044", $processed);
			}
			return array(array_slice($words, $i), $processed);
		}
		return array($words, array());
	}
	
	#Attempts to find a Compound at the start of the word list. This is recursive.
	#Return: [remaining words, consumed words]
	function captureCompound($words){
		global $generation;
		global $valid;
		global $reason;
		
		if(count($words) == 0){#[nil]
			return array($words, array());
		}
		
		$processed_total = array();
		
		#Attempt to match [O].
		list($remainder, $processed, $is_oo) = captureNounPhrase($words, false, false, true);
		$processed_total = array_merge($processed_total, $processed);
		if($remainder == $words && $generation == 2){#Allow EV in place of O.
			list($remainder, $processed) = captureEmotionVerbPhrase($remainder, false, false);
			$processed_total = array_merge($processed_total, $processed);
		}
		
		if($remainder == $words){#Not [O], so attempt to match [V].
			list($remainder, $processed) = captureVerbPhrase($words, true, false);
			$processed_total = array_merge($processed_total, $processed);
			if($valid){#[V] formed.
				list($rest, $processed, $is_oo) = captureNounPhrase($remainder, false, false);
				$processed_total = array_merge($processed_total, $processed);
				if($remainder == $rest && $generation == 2){#Allow EV in place of O.
					list($rest, $processed) = captureEmotionVerbPhrase($remainder, false, false);
					$processed_total = array_merge($processed_total, $processed);
				}
				if($is_oo){#If [VOO], then processing is complete.
					return array($rest, $processed_total);
				}elseif($rest != $remainder){#[VO] formed.
					list($remainder, $processed, $is_oo) = captureNounPhrase($rest, false, false, true);
					$processed_total = array_merge($processed_total, $processed);
					if($rest == $remainder && $generation == 2){#Allow EV in place of O.
						list($remainder, $processed) = captureEmotionVerbPhrase($rest, false, false);
						$processed_total = array_merge($processed_total, $processed);
					}
					if($rest != $remainder){#[VOO] formed.
						return array($remainder, $processed_total);
					}else{#[VOC] O not found, so check for another compound.
						list($remainder, $processed) = captureCompound($remainder);
						$processed_total = array_merge($processed_total, $processed);
					}
				}else{#[VC] found.
					list($remainder, $processed) = captureCompound($rest);
					$processed_total = array_merge($processed_total, $processed);
				}
			}
		}
		
		return array($remainder, $processed_total);
	}
?>
<table style="border-collapse: collapse; border: 1px solid black; width: 640px;">
	<tr>
		<td style="color: darkblue; text-align: center; background: lightgrey;" colspan="2">
			<span style="font-family: hymmnos; font-size: 24pt;">
				<?php echo $word_string; ?>
			</span>
			<br/>
			<span style="font-size: 18pt;">
				<?php echo $word_string; ?>
			</span>
		</td>
	</tr>
	<?php evaluateWords($words); ?>
	<tr>
		<?php
			if($valid){#Inform the user of the validity of their sentence.
				echo '<td style="background: blue; color: white; text-align: center;" colspan="2">';
					echo '<big>This sentence appears to be valid Hymmnos</big><br/>';
					echo '<small>(Component division may be inaccurate; when in doubt, check the Japanese form)</small>';
				echo '</td>';
			}else{
				echo '<td style="background: red; color: white; text-align: center;" colspan="2">';
					echo '<big>This sentence does not appear to be valid Hymmnos</big><br/>';
					echo "<small>Reason: $reason.</small>";
				echo '</td>';
			}
		?>
	</tr>
</table>
<hr/>
<div style="color: grey; font-size: 0.6em;">
	<p>
		There is no difference between singular and plural nouns, unless implied by context:
		&quot;wart&quot;, for example, can mean either &quot;word&quot; or &quot;words&quot;,
		depending on which is more appropriate.<br/>
	</p>
	<p>
		The presented kana does not take Emotion Vowels into consideration.
	</p>
	<p>
		Only the more basic rules of the Hymmnos grammar are validated by this system at this time.
		Additionally, you may find that problems arise when you attempt to use complex conjunctions;
		this is likely not because you made a mistake, but rather because this system does not
		currently employ syntax trees to map language elements (it uses a linear analyzer because such
		an approach seemed sufficient to match (and exceed) the Japanese site).
		<a href="http://weezy.freeforums.org/hymmnoserver-english-translation-grammar-evaluator-thingy-t729.html">Planning for an improved version</a>
		is underway.
	</p>
</div>