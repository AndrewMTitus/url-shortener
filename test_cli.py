from click.testing import CliRunner
from cli import cli

def test_shorten():
    runner = CliRunner()
    result = runner.invoke(cli, ['shorten', '--url', 'https://example.com'])
    assert result.exit_code == 0
    assert 'Shortened URL' in result.output

