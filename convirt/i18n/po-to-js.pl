#!/usr/bin/perl -w

use strict;
use HTML::Entities;

my %langs = (
    'be_BY' => 'be',
    'cy_GB' => 'cy',
    'de_DE' => 'de',
    'en_GB' => 'en-gb',
    'en'    => 'en',
    'eo_XX' => 'eo',
    'es_ES' => 'es',
    'et_EE' => 'et',
    'fi_FI' => 'fi',
    'fr_FR' => 'fr',
    'it_IT' => 'it',
    'ja_JP' => 'ja',
    'nl_BE' => 'nl-be',
    'nl_NL' => 'nl',
    'pa_IN' => 'pa',
    'pl_PL' => 'pl',
    'pt_BR' => 'pt-br',
    'ru'    => 'ru',
    'ru_RU' => 'ru',
    'sk_SK' => 'sk',
    'tr'    => 'tr',
    'uk_UA' => 'uk',
    'zh_CN' => 'zh'
);

for (<./*/LC_MESSAGES/convirt*.po>) {
    my ($lang) = /\/(.*?)\//;
    #my ($microsite) = /convirt-(.*?)\.po$/;
    #print $lang . " $microsite\n";
    open(FP, $_) or die $!;
    my $out = '';
    my $next = '';
    while ($next = <FP>) {
        my $msgid = '';
        if ($next =~ /^msgid /) {
            ($msgid) = $next =~ /^msgid "(.*)"/;
            my $l;
            while (($l = <FP>) !~ /^msgstr/) {
                chomp($l);
                $msgid .= substr($l, 1, -1);
            }
            $next = $l;
            if ($msgid =~ /^\s*$/) {
                next;
            }
            my $msgstr = '';
            if ($next =~ /^msgstr /) {
                ($msgstr) = $next =~ /^msgstr "(.*)"/;
                while ((my $l = <FP>) !~ /^\s+$/) {
                    chomp($l);
                    $msgstr .= substr($l, 1, -1);
                }
            } 
            _decode_entities($msgstr, { nbsp => "\xc2\xa0", ocirc => "\xc3\xb4" });
            $out .= "i18n[\"$msgid\"] = \"$msgstr\";\n";
        }
    }
    close FP;
    $out = substr($out, 0, -2);
    open (FP, ">../public/javascript/ext2.2.1/resources/locale/convirt-lang-$langs{$lang}.js") or die $!;
    print FP <<EOF;
/*
 * convirt-lang-$langs{$lang}.js
 * Translation of JS strings
 * Auto-generated from .po files
 */

if (typeof(i18n) == 'undefined') {
    var i18n = Array()
}

EOF
    print FP $out;
    close FP;
}


