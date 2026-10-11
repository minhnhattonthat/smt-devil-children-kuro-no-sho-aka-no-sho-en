import lint


def test_all_translated_event_text_passes_lint():
    assert lint.main.__module__ == 'lint'
    import sys
    argv = sys.argv
    sys.argv = ['lint.py', '--all']
    try:
        assert lint.main() == 0
    finally:
        sys.argv = argv


def test_wrap_keeps_two_lines_and_balances():
    w = lint.wrap('Anyone who inherits that man\'s blood is nothing but a nuisance to my plan.{wait}{end}')
    lines = w.split('{n}')
    assert len(lines) == 2
    assert all(lint.text_width(lint.TOKEN.sub('', ln)) <= 224 for ln in lines)


def test_choice_gets_cursor_indent_and_no_wrap():
    jp = '　赤いデビル{n}　白いデビル{n}　黒いデビル{end}'
    assert lint.form(jp) == 'choice'
    assert lint.prepare(jp, 'Red Devil{n}White Devil{n}Black Devil{end}') == \
        '[0000]Red Devil{n}[0000]White Devil{n}[0000]Black Devil{end}'
    assert lint.lint_event(jp, 'Red Devil{n}White Devil{end}')  # option count differs
