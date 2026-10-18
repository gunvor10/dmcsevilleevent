<?php
// DMC Seville Event – contact form handler (www.dmcsevilleevent.com/contact/send.php)
// Spam filters: honeypot, JavaScript time token, no web links, rate limit per IP, required fields.
// Sends the enquiry to events@dmcsevilleevent.com; the customer is set as Reply-To.

const TO = 'events@dmcsevilleevent.com';
const FROM = 'web@dmcsevilleevent.com';
const THANKS = '/contact/thank-you/';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { header('Location: /contact/', true, 303); exit; }

function field($k, $max = 500) {
    $v = isset($_POST[$k]) ? trim((string) $_POST[$k]) : '';
    $v = str_replace(["\r", "\0"], '', $v);
    return mb_substr($v, 0, $max);
}
function back($err) { header('Location: /contact/?error=' . urlencode($err) . '#enquiry', true, 303); exit; }
function thanks() { header('Location: ' . THANKS, true, 303); exit; }

// 1. honeypot: only robots fill in the hidden field -> pretend all is fine
if (field('website') !== '') thanks();

// 2. time token set by JavaScript when the page loads (robots without JS send none)
$t = (int) field('t', 20);
$age = (int) round(microtime(true) * 1000) - $t;
if ($t <= 0) thanks();
if ($age < 4000) back('fast');

// 3. rate limit: max 4 requests per IP per hour
$ip = $_SERVER['REMOTE_ADDR'] ?? '';
$rl = sys_get_temp_dir() . '/dmc_enq_' . md5($ip);
$hits = array_filter(is_file($rl) ? (array) json_decode((string) file_get_contents($rl), true) : [], function ($x) { return $x > time() - 3600; });
if (count($hits) >= 4) back('limit');

$d = [
    'name' => field('name', 120), 'company' => field('company', 120), 'email' => field('email', 120),
    'phone' => field('phone', 40), 'type' => field('type', 60), 'guests' => field('guests', 10),
    'dates' => field('dates', 80), 'activity' => field('activity', 120), 'message' => field('message', 4000),
    'page' => field('page', 300),
];
if ($d['name'] === '' || $d['email'] === '' || $d['type'] === '' || $d['guests'] === '' || $d['message'] === '') back('missing');
if (!filter_var($d['email'], FILTER_VALIDATE_EMAIL)) back('email');
if (field('consent') !== '1') back('consent');
// 4. no web links (spam almost always contains links)
if (preg_match('#(https?://|www\.|\[url|<a\s)#i', $d['message'] . ' ' . $d['name'] . ' ' . $d['company'])) back('links');
foreach (['name', 'email', 'company'] as $k) $d[$k] = str_replace("\n", ' ', $d[$k]);

$subject = 'Website enquiry – ' . $d['type'] . ' – ' . $d['guests'] . ' guests' . ($d['dates'] ? ' – ' . $d['dates'] : '') . ' – ' . $d['name'];
$body = "New enquiry from www.dmcsevilleevent.com\n\n"
    . "Name: {$d['name']}\nCompany: {$d['company']}\nE-mail: {$d['email']}\nPhone/WhatsApp: {$d['phone']}\n"
    . "Type of event: {$d['type']}\nGuests: {$d['guests']}\nDates: {$d['dates']}\nActivity: {$d['activity']}\n\n"
    . "Message:\n{$d['message']}\n\n---\nSent from: {$d['page']}\nIP: $ip\nTime: " . date('Y-m-d H:i') . "\n";
$enc = '=?UTF-8?B?' . base64_encode($subject) . '?=';
$headers = "From: DMC Seville Event website <" . FROM . ">\r\n"
    . "Reply-To: " . '=?UTF-8?B?' . base64_encode($d['name']) . '?=' . " <{$d['email']}>\r\n"
    . "MIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: 8bit\r\n";
$ok = mail(TO, $enc, $body, $headers, '-f' . FROM);

$hits[] = time();
@file_put_contents($rl, json_encode(array_values($hits)));
if (!$ok) back('send');
thanks();
