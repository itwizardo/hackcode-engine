//! Automatic PDF report generation for HackCode security audits.
//!
//! After each AI turn, if the response looks like a security audit or
//! vulnerability report, this module generates a clean PDF and saves it
//! to the current working directory.

use std::io::Write;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

const GREEN: &str = "\x1b[38;2;0;255;65m";
const DIM: &str = "\x1b[90m";
const BOLD: &str = "\x1b[1m";
const RESET: &str = "\x1b[0m";

/// Strong indicators — phrases that only appear in actual audit reports,
/// not in casual "what can you do?" capability listings.
const REPORT_PHRASES: &[&str] = &[
    "security audit",
    "penetration test",
    "security report",
    "audit report",
    "threat assessment",
    "vulnerability assessment",
    "security assessment",
];

/// Finding-level keywords that signal real scan results (not capabilities).
const FINDING_KEYWORDS: &[&str] = &[
    "cve-",
    "critical risk",
    "high risk",
    "medium risk",
    "low risk",
    "severity:",
    "finding:",
    "hardcoded secret",
    "misconfiguration",
    "open port",
    "exposed service",
];

/// Past-tense / results language — real reports describe what was found.
const RESULTS_LANGUAGE: &[&str] = &[
    "found",
    "detected",
    "discovered",
    "identified",
    "vulnerable to",
    "is exposed",
    "was found",
    "were found",
    "recommendation",
    "remediation",
];

/// Minimum response length to consider for report generation.
const MIN_REPORT_LENGTH: usize = 600;

/// Check if the AI response looks like a security audit report.
///
/// To avoid false positives on casual capability listings, we require:
///   - At least 1 report-level phrase (e.g. "security audit"), AND
///   - At least 2 finding-level keywords (e.g. "cve-", "high risk"), AND
///   - At least 1 results-language marker (e.g. "found", "detected")
pub fn is_audit_report(text: &str) -> bool {
    if text.len() < MIN_REPORT_LENGTH {
        return false;
    }
    let lower = text.to_lowercase();

    let has_report_phrase = REPORT_PHRASES.iter().any(|kw| lower.contains(kw));
    let finding_hits = FINDING_KEYWORDS
        .iter()
        .filter(|kw| lower.contains(*kw))
        .count();
    let has_results_lang = RESULTS_LANGUAGE.iter().any(|kw| lower.contains(kw));

    has_report_phrase && finding_hits >= 2 && has_results_lang
}

/// Strip ANSI escape codes from text.
fn strip_ansi(text: &str) -> String {
    let mut result = String::with_capacity(text.len());
    let mut chars = text.chars().peekable();
    while let Some(ch) = chars.next() {
        if ch == '\x1b' {
            // Skip until we hit a letter (end of escape sequence)
            while let Some(&next) = chars.peek() {
                chars.next();
                if next.is_ascii_alphabetic() {
                    break;
                }
            }
        } else {
            result.push(ch);
        }
    }
    result
}

/// Generate a PDF report from the AI's response text.
/// Returns the path to the generated PDF file.
pub fn generate_report(text: &str) -> Result<PathBuf, String> {
    let clean_text = strip_ansi(text);

    // Generate filename with timestamp
    let timestamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();

    let date = format_date(timestamp);
    let filename = format!("hackcode-report-{date}.pdf");
    let output_path = std::env::current_dir()
        .unwrap_or_else(|_| PathBuf::from("."))
        .join(&filename);

    // Build the PDF
    let pdf_bytes = build_pdf(&clean_text, &date)
        .map_err(|e| format!("Failed to generate PDF: {e}"))?;

    std::fs::write(&output_path, &pdf_bytes)
        .map_err(|e| format!("Failed to write PDF: {e}"))?;

    Ok(output_path)
}

/// Print the report saved notification.
pub fn print_report_saved(path: &Path) {
    let display = path.display();
    println!(
        "\n{GREEN}[HackCode]{RESET} {BOLD}Security report saved{RESET} → {DIM}{display}{RESET}"
    );
}

/// Format a unix timestamp into YYYY-MM-DD-HHMMSS.
fn format_date(secs: u64) -> String {
    // Simple date formatting without chrono dependency.
    // Convert epoch seconds to date components.
    let days = secs / 86400;
    let time_of_day = secs % 86400;
    let hours = time_of_day / 3600;
    let minutes = (time_of_day % 3600) / 60;
    let seconds = time_of_day % 60;

    // Days since epoch to year/month/day (simplified Gregorian).
    let (year, month, day) = days_to_ymd(days);

    format!(
        "{year:04}-{month:02}-{day:02}-{hours:02}{minutes:02}{seconds:02}"
    )
}

fn days_to_ymd(mut days: u64) -> (u64, u64, u64) {
    // Algorithm from http://howardhinnant.github.io/date_algorithms.html
    days += 719468;
    let era = days / 146097;
    let doe = days - era * 146097;
    let yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
    let y = yoe + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = doy - (153 * mp + 2) / 5 + 1;
    let m = if mp < 10 { mp + 3 } else { mp - 9 };
    let y = if m <= 2 { y + 1 } else { y };
    (y, m, d)
}

// ── Minimal PDF builder ──────────────────────────────────────────────
//
// Generates a valid PDF 1.4 document with embedded Helvetica text.
// No external crate needed — just raw PDF spec.

struct PdfBuilder {
    objects: Vec<Vec<u8>>,
}

impl PdfBuilder {
    fn new() -> Self {
        Self {
            objects: Vec::new(),
        }
    }

    fn add_object(&mut self, data: Vec<u8>) -> usize {
        self.objects.push(data);
        self.objects.len() // 1-based object number
    }

    fn build(
        &mut self,
        pages_obj: usize,
        page_objs: &[usize],
        catalog_obj: usize,
    ) -> Vec<u8> {
        let mut out = Vec::new();
        out.extend_from_slice(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n");

        let mut offsets = Vec::new();

        for (i, obj) in self.objects.iter().enumerate() {
            offsets.push(out.len());
            write!(out, "{} 0 obj\n", i + 1).unwrap();
            out.extend_from_slice(obj);
            out.extend_from_slice(b"\nendobj\n");
        }

        // Cross-reference table
        let xref_offset = out.len();
        write!(out, "xref\n0 {}\n", self.objects.len() + 1).unwrap();
        write!(out, "0000000000 65535 f \n").unwrap();
        for offset in &offsets {
            write!(out, "{:010} 00000 n \n", offset).unwrap();
        }

        // Trailer
        write!(
            out,
            "trailer\n<< /Size {} /Root {} 0 R >>\nstartxref\n{}\n%%EOF\n",
            self.objects.len() + 1,
            catalog_obj,
            xref_offset
        )
        .unwrap();

        out
    }
}

/// Wrap text to fit within page width (~80 chars for Helvetica 10pt).
fn wrap_lines(text: &str, max_chars: usize) -> Vec<String> {
    let mut lines = Vec::new();
    for line in text.lines() {
        if line.len() <= max_chars {
            lines.push(line.to_string());
        } else {
            // Word wrap
            let mut current = String::new();
            for word in line.split_whitespace() {
                if current.len() + word.len() + 1 > max_chars {
                    if !current.is_empty() {
                        lines.push(current);
                    }
                    current = word.to_string();
                } else {
                    if !current.is_empty() {
                        current.push(' ');
                    }
                    current.push_str(word);
                }
            }
            if !current.is_empty() {
                lines.push(current);
            }
        }
    }
    lines
}

/// Escape special PDF string characters.
fn pdf_escape(s: &str) -> String {
    s.replace('\\', "\\\\")
        .replace('(', "\\(")
        .replace(')', "\\)")
}

/// Build a PDF document from the report text.
fn build_pdf(text: &str, date: &str) -> Result<Vec<u8>, std::fmt::Error> {
    let mut pdf = PdfBuilder::new();

    // Fixed metrics for Helvetica at various sizes
    let line_height = 13.0_f32; // 10pt text + 3pt leading
    let title_height = 22.0_f32;
    let margin_top = 50.0;
    let margin_bottom = 60.0;
    let margin_left = 50.0;
    let page_width = 612.0_f32; // US Letter
    let page_height = 792.0_f32;
    let usable_height = page_height - margin_top - margin_bottom;
    let max_chars_per_line = 90;

    // Wrap all text into lines
    let all_lines = wrap_lines(text, max_chars_per_line);

    // Calculate how many lines fit per page (first page has title)
    let first_page_lines =
        ((usable_height - title_height - 20.0) / line_height) as usize;
    let normal_page_lines = (usable_height / line_height) as usize;

    // Split into pages
    let mut pages_content: Vec<Vec<&str>> = Vec::new();
    let mut idx = 0;

    // First page
    let end = std::cmp::min(idx + first_page_lines, all_lines.len());
    pages_content.push(all_lines[idx..end].iter().map(|s| s.as_str()).collect());
    idx = end;

    // Remaining pages
    while idx < all_lines.len() {
        let end = std::cmp::min(idx + normal_page_lines, all_lines.len());
        pages_content.push(all_lines[idx..end].iter().map(|s| s.as_str()).collect());
        idx = end;
    }

    // Object 1: Font (Helvetica)
    let font_obj = pdf.add_object(
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>".to_vec(),
    );

    // Object 2: Bold font (Helvetica-Bold)
    let font_bold_obj = pdf.add_object(
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>".to_vec(),
    );

    // Reserve pages object number (we'll fill it in later)
    let pages_placeholder = pdf.add_object(b"<< >>".to_vec());

    // Create page objects
    let mut page_objs = Vec::new();

    for (page_idx, page_lines) in pages_content.iter().enumerate() {
        // Build the content stream
        let mut stream = Vec::new();

        if page_idx == 0 {
            // Title
            write!(
                stream,
                "BT\n/F2 16 Tf\n{} {} Td\n({}) Tj\nET\n",
                margin_left,
                page_height - margin_top,
                pdf_escape("HACKCODE SECURITY AUDIT REPORT")
            )
            .unwrap();

            // Date line
            write!(
                stream,
                "BT\n/F1 9 Tf\n0.5 0.5 0.5 rg\n{} {} Td\n({}) Tj\n0 0 0 rg\nET\n",
                margin_left,
                page_height - margin_top - 18.0,
                pdf_escape(&format!("Generated by HackCode — {date}"))
            )
            .unwrap();

            // Separator line
            let line_y = page_height - margin_top - 28.0;
            write!(
                stream,
                "0.8 0.8 0.8 RG\n0.5 w\n{} {} m {} {} l S\n",
                margin_left,
                line_y,
                page_width - margin_left,
                line_y
            )
            .unwrap();

            // Body text
            let start_y = page_height - margin_top - title_height - 20.0;
            write!(stream, "BT\n/F1 10 Tf\n").unwrap();
            write!(stream, "{} {} Td\n", margin_left, start_y).unwrap();

            for (i, line) in page_lines.iter().enumerate() {
                if i > 0 {
                    write!(stream, "0 -{} Td\n", line_height).unwrap();
                }

                // Detect section headers (ALL CAPS lines or lines starting with ##)
                let trimmed = line.trim();
                if is_section_header(trimmed) {
                    write!(stream, "/F2 11 Tf\n").unwrap();
                    write!(stream, "({}) Tj\n", pdf_escape(trimmed)).unwrap();
                    write!(stream, "/F1 10 Tf\n").unwrap();
                } else {
                    write!(stream, "({}) Tj\n", pdf_escape(line)).unwrap();
                }
            }
            write!(stream, "ET\n").unwrap();
        } else {
            // Subsequent pages — body only
            let start_y = page_height - margin_top;
            write!(stream, "BT\n/F1 10 Tf\n").unwrap();
            write!(stream, "{} {} Td\n", margin_left, start_y).unwrap();

            for (i, line) in page_lines.iter().enumerate() {
                if i > 0 {
                    write!(stream, "0 -{} Td\n", line_height).unwrap();
                }
                let trimmed = line.trim();
                if is_section_header(trimmed) {
                    write!(stream, "/F2 11 Tf\n").unwrap();
                    write!(stream, "({}) Tj\n", pdf_escape(trimmed)).unwrap();
                    write!(stream, "/F1 10 Tf\n").unwrap();
                } else {
                    write!(stream, "({}) Tj\n", pdf_escape(line)).unwrap();
                }
            }
            write!(stream, "ET\n").unwrap();

            // Page number footer
            let page_num = page_idx + 1;
            let total = pages_content.len();
            write!(
                stream,
                "BT\n/F1 8 Tf\n0.5 0.5 0.5 rg\n{} 30 Td\n({}) Tj\nET\n",
                page_width / 2.0 - 20.0,
                pdf_escape(&format!("Page {page_num} of {total}"))
            )
            .unwrap();
        }

        // Content stream object
        let stream_len = stream.len();
        let mut stream_obj = Vec::new();
        write!(
            stream_obj,
            "<< /Length {} >>\nstream\n",
            stream_len
        )
        .unwrap();
        stream_obj.extend_from_slice(&stream);
        stream_obj.extend_from_slice(b"\nendstream");
        let content_obj = pdf.add_object(stream_obj);

        // Page object
        let mut page_data = Vec::new();
        write!(
            page_data,
            "<< /Type /Page /Parent {} 0 R /MediaBox [0 0 {} {}] /Contents {} 0 R /Resources << /Font << /F1 {} 0 R /F2 {} 0 R >> >> >>",
            pages_placeholder,
            page_width,
            page_height,
            content_obj,
            font_obj,
            font_bold_obj
        )
        .unwrap();
        let page_obj = pdf.add_object(page_data);
        page_objs.push(page_obj);
    }

    // Fill in the Pages object
    let mut kids = String::from("[");
    for (i, obj) in page_objs.iter().enumerate() {
        if i > 0 {
            kids.push(' ');
        }
        kids.push_str(&format!("{} 0 R", obj));
    }
    kids.push(']');

    let pages_data = format!(
        "<< /Type /Pages /Kids {} /Count {} >>",
        kids,
        page_objs.len()
    );
    pdf.objects[pages_placeholder - 1] = pages_data.into_bytes();

    // Catalog object
    let catalog_data = format!(
        "<< /Type /Catalog /Pages {} 0 R >>",
        pages_placeholder
    );
    let catalog_obj = pdf.add_object(catalog_data.into_bytes());

    Ok(pdf.build(pages_placeholder, &page_objs, catalog_obj))
}

/// Detect if a line looks like a section header.
fn is_section_header(line: &str) -> bool {
    if line.is_empty() {
        return false;
    }
    // Markdown headers
    if line.starts_with('#') {
        return true;
    }
    // ALL CAPS lines (with at least 3 alpha chars)
    let alpha_count = line.chars().filter(|c| c.is_ascii_alphabetic()).count();
    if alpha_count >= 3 && line.chars().filter(|c| c.is_ascii_alphabetic()).all(|c| c.is_ascii_uppercase()) {
        return true;
    }
    // Lines ending with colon that look like headers
    if line.ends_with(':') && line.len() < 60 && !line.contains('.') {
        return true;
    }
    false
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_is_audit_report_positive() {
        let text = "# SECURITY AUDIT REPORT\n\
            ## Threat Assessment\n\
            Found multiple vulnerability issues including SQL injection.\n\
            Severity: HIGH. The exploit allows remote code execution.\n\
            Findings include hardcoded secret keys and misconfiguration.\n"
            .repeat(3);
        assert!(is_audit_report(&text));
    }

    #[test]
    fn test_is_audit_report_negative() {
        let text = "Hello! I listed all the files in this directory. Here they are:";
        assert!(!is_audit_report(text));
    }

    #[test]
    fn test_strip_ansi() {
        let input = "\x1b[38;5;12mhello\x1b[0m world";
        assert_eq!(strip_ansi(input), "hello world");
    }

    #[test]
    fn test_wrap_lines() {
        let text = "this is a very long line that should definitely be wrapped at some reasonable point";
        let wrapped = wrap_lines(text, 30);
        assert!(wrapped.len() > 1);
        for line in &wrapped {
            assert!(line.len() <= 35); // some tolerance for word boundaries
        }
    }

    #[test]
    fn test_pdf_escape() {
        assert_eq!(pdf_escape("hello (world)"), "hello \\(world\\)");
        assert_eq!(pdf_escape("back\\slash"), "back\\\\slash");
    }

    #[test]
    fn test_section_header_detection() {
        assert!(is_section_header("## EXECUTIVE SUMMARY"));
        assert!(is_section_header("THREAT ASSESSMENT"));
        assert!(is_section_header("Findings:"));
        assert!(!is_section_header("This is a normal line."));
        assert!(!is_section_header(""));
    }

    #[test]
    fn test_build_pdf_valid() {
        let text = "# Security Report\n\nFound 3 vulnerabilities.\n\n## HIGH: SQL Injection\nThe login form is vulnerable.";
        let pdf = build_pdf(text, "2026-04-13").unwrap();
        // Valid PDF starts with %PDF-
        assert!(pdf.starts_with(b"%PDF-1.4"));
        // Valid PDF ends with %%EOF
        let tail = String::from_utf8_lossy(&pdf[pdf.len() - 10..]);
        assert!(tail.contains("%%EOF"));
    }
}
