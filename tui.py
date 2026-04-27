from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Label, Select
from textual.containers import Vertical, Horizontal
from textual.widget import Widget
from textual.reactive import reactive
from rich.text import Text
from rankconverter import convertRank, osDivToRank, rankPrefix

TIER_COLORS_NS = ["#cd7f32", "#c0c0c0", "#ffd700", "#a0b0b0", "#4169e1", "#00a550", "#9b59b6", "#ff69b4"]
TIER_COLORS_OS = ["#cd7f32", "#c0c0c0", "#ffd700", "#a0b0b0", "#4169e1", "#00a550", "#9b59b6"]

TIER_COLORS_MAP = {
    "Bronze": "#cd7f32",
    "Silver": "#c0c0c0",
    "Gold": "#ffd700",
    "Platinum": "#a0b0b0",
    "Diamond": "#4169e1",
    "Master": "#00a550",
    "Grandmaster": "#9b59b6",
    "Champion": "#ff69b4"
}

class RankBar(Widget):
    marker_pos: reactive[float] = reactive(0.0)

    def __init__(self, colors: list, **kwargs):
        super().__init__(**kwargs)
        self._colors = colors

    def render(self) -> Text:
        width = self.size.width
        segments = len(self._colors)
        seg_width = width // segments
        remainder = width - (seg_width * segments)

        bar = Text()
        for i, color in enumerate(self._colors):
            extra = 1 if i < remainder else 0
            bar.append("█" * (seg_width + extra), style=color)

        marker_x = int(self.marker_pos * width)
        marker_line = Text()
        marker_line.append(" " * marker_x)
        marker_line.append("▲", style="white bold")

        return Text.assemble(bar, "\n", marker_line)


def rankToSR(tier: str, div: int, percent: int) -> int:
    tier_index = rankPrefix.index(tier)
    tier_base = 1000 + (tier_index * 500)
    div_base = (5 - div) * 100
    sr = tier_base + div_base + percent
    return sr


class RankConverter(App):
    CSS_PATH = "tui.tcss"
    BINDINGS = [("ctrl+r", "reset", "Reset")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with Vertical(id="container"):
            yield Label("OW Rank Converter", id="title")
            with Horizontal(id="input_row"):
                yield Select(
                    [(t, t) for t in rankPrefix],
                    prompt="Tier",
                    id="tier_select"
                )
                yield Select(
                    [(str(d), d) for d in range(5, 0, -1)],
                    prompt="Div",
                    id="div_select"
                )
                yield Input(placeholder="% (0-99)", id="percent_input")
            yield Label("Current Rank: —", id="ns_label")
            yield Label("Legacy Rank: —", id="os_label")
            yield RankBar(TIER_COLORS_NS, id="ns_bar")
            yield RankBar(TIER_COLORS_OS, id="os_bar")

    def update_ranks(self) -> None:
        try:
            tier_select = self.query_one("#tier_select", Select)
            div_select = self.query_one("#div_select", Select)
            percent_input = self.query_one("#percent_input", Input)

            if tier_select.value is Select.BLANK or div_select.value is Select.BLANK:
                return
            if not percent_input.value:
                return

            tier = tier_select.value
            div = int(div_select.value)
            percent = int(percent_input.value)

            if not 0 <= percent <= 99:
                return

            nsRank = rankToSR(tier, div, percent)
            osDiv = convertRank(nsRank)
            rank = osDivToRank(osDiv)

            ns_color = TIER_COLORS_MAP[tier]
            os_color = TIER_COLORS_MAP[rank["tier"]]

            ns_label = self.query_one("#ns_label", Label)
            os_label = self.query_one("#os_label", Label)

            ns_label.update(f"Current Rank: [{ns_color}]{tier} {div} {percent}%[/] ({nsRank} SR)")
            os_label.update(f"Legacy Rank: [{os_color}]{rank['tier']} {rank['div']} {rank['percent']}%[/]")

            self.query_one("#ns_bar", RankBar).marker_pos = (nsRank - 1000) / 4000
            self.query_one("#os_bar", RankBar).marker_pos = osDiv / 35

        except (ValueError, Exception):
            pass

    def action_reset(self) -> None:
        self.query_one("#tier_select", Select).clear()
        self.query_one("#div_select", Select).clear()
        self.query_one("#percent_input", Input).value = ""
        self.query_one("#ns_label", Label).update("Current Rank: —")
        self.query_one("#os_label", Label).update("Legacy Rank: —")
        self.query_one("#ns_bar", RankBar).marker_pos = 0.0
        self.query_one("#os_bar", RankBar).marker_pos = 0.0

    def on_select_changed(self, event: Select.Changed) -> None:
        self.update_ranks()

    def on_input_changed(self, event: Input.Changed) -> None:
        self.update_ranks()


if __name__ == "__main__":
    app = RankConverter()
    app.run()