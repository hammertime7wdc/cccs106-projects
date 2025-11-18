"""Weather Application using Flet v0.28.3 with Search History, Unit Toggle, and Dynamic Themes"""

import flet as ft
from weather_service import WeatherService
from config import Config
import json
from pathlib import Path


class WeatherApp:
    """Main Weather Application class."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        
        # Initialize search history
        self.history_file = Path("search_history.json")
        self.search_history = self.load_history()
        
        # Initialize temperature unit preference
        self.preferences_file = Path("preferences.json")
        self.current_unit = self.load_preferences()
        
        # Store current weather data for unit conversion
        self.current_weather_data = None
        
        self.setup_page()
        self.build_ui()
    
    def load_history(self):
        """Load search history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []
    
    def save_history(self):
        """Save search history to file."""
        with open(self.history_file, 'w') as f:
            json.dump(self.search_history, f)
    
    def load_preferences(self):
        """Load user preferences from file."""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r') as f:
                    prefs = json.load(f)
                    return prefs.get("unit", "metric")
            except json.JSONDecodeError:
                return "metric"
        return "metric"
    
    def save_preferences(self):
        """Save user preferences to file."""
        with open(self.preferences_file, 'w') as f:
            json.dump({"unit": self.current_unit}, f)
    
    def add_to_history(self, city: str):
        """Add city to history (avoid duplicates and keep last 10)."""
        city = city.strip()
        if city:
            # Remove if already exists to avoid duplicates
            if city in self.search_history:
                self.search_history.remove(city)
            
            # Add to beginning
            self.search_history.insert(0, city)
            
            # Keep only last 10 searches
            self.search_history = self.search_history[:10]
            
            # Save to file
            self.save_history()
            
            # Update the dropdown
            self.update_history_dropdown()
    
    def update_history_dropdown(self):
        """Update the history dropdown with current history."""
        if self.search_history:
            self.history_dropdown.options = [
                ft.dropdown.Option(city) for city in self.search_history
            ]
            self.history_dropdown.visible = True
        else:
            self.history_dropdown.visible = False
        self.page.update()
    
    def on_history_select(self, e):
        """Handle history item selection."""
        if e.control.value:
            self.city_input.value = e.control.value
            self.page.update()
            # Automatically search for the selected city
            self.page.run_task(self.get_weather)
    
    def get_weather_colors(self, weather_main: str, icon_code: str):
        """Return colors and emoji based on weather condition."""
        weather_main = weather_main.lower()
        is_night = icon_code.endswith('n')
        
        weather_themes = {
            'clear': {
                'bg': ft.Colors.AMBER_50 if not is_night else ft.Colors.BLUE_GREY_900,
                'accent': ft.Colors.ORANGE_700 if not is_night else ft.Colors.BLUE_GREY_400,
                'emoji': '☀️' if not is_night else '🌙',
                'gradient_start': ft.Colors.AMBER_100 if not is_night else ft.Colors.BLUE_GREY_800,
                'gradient_end': ft.Colors.ORANGE_100 if not is_night else ft.Colors.BLUE_GREY_900,
            },
            'clouds': {
                'bg': ft.Colors.BLUE_GREY_50,
                'accent': ft.Colors.BLUE_GREY_700,
                'emoji': '☁️',
                'gradient_start': ft.Colors.BLUE_GREY_100,
                'gradient_end': ft.Colors.BLUE_GREY_200,
            },
            'rain': {
                'bg': ft.Colors.BLUE_50,
                'accent': ft.Colors.BLUE_800,
                'emoji': '🌧️',
                'gradient_start': ft.Colors.BLUE_100,
                'gradient_end': ft.Colors.BLUE_200,
            },
            'drizzle': {
                'bg': ft.Colors.LIGHT_BLUE_50,
                'accent': ft.Colors.LIGHT_BLUE_700,
                'emoji': '🌦️',
                'gradient_start': ft.Colors.LIGHT_BLUE_100,
                'gradient_end': ft.Colors.LIGHT_BLUE_200,
            },
            'thunderstorm': {
                'bg': ft.Colors.DEEP_PURPLE_100,
                'accent': ft.Colors.DEEP_PURPLE_900,
                'emoji': '⛈️',
                'gradient_start': ft.Colors.DEEP_PURPLE_200,
                'gradient_end': ft.Colors.DEEP_PURPLE_300,
            },
            'snow': {
                'bg': ft.Colors.CYAN_50,
                'accent': ft.Colors.CYAN_900,
                'emoji': '❄️',
                'gradient_start': ft.Colors.CYAN_50,
                'gradient_end': ft.Colors.LIGHT_BLUE_50,
            },
            'mist': {
                'bg': ft.Colors.GREY_100,
                'accent': ft.Colors.GREY_700,
                'emoji': '🌫️',
                'gradient_start': ft.Colors.GREY_100,
                'gradient_end': ft.Colors.GREY_200,
            },
            'fog': {
                'bg': ft.Colors.GREY_100,
                'accent': ft.Colors.GREY_700,
                'emoji': '🌫️',
                'gradient_start': ft.Colors.GREY_100,
                'gradient_end': ft.Colors.GREY_200,
            },
            'haze': {
                'bg': ft.Colors.GREY_100,
                'accent': ft.Colors.GREY_600,
                'emoji': '🌫️',
                'gradient_start': ft.Colors.GREY_100,
                'gradient_end': ft.Colors.GREY_200,
            },
        }
        
        # Return theme or default
        return weather_themes.get(weather_main, weather_themes['clear'])
    
    def convert_temp(self, temp_celsius: float):
        """Convert temperature based on current unit."""
        if self.current_unit == "imperial":
            return (temp_celsius * 9/5) + 32
        return temp_celsius
    
    def get_temp_symbol(self):
        """Get temperature symbol based on current unit."""
        return "°F" if self.current_unit == "imperial" else "°C"
    
    def toggle_units(self, e):
        """Toggle between Celsius and Fahrenheit."""
        # Toggle unit
        self.current_unit = "imperial" if self.current_unit == "metric" else "metric"
        
        # Save preference
        self.save_preferences()
        
        # Update button text
        self.unit_toggle.text = "°C" if self.current_unit == "imperial" else "°F"
        self.page.update()
        
        # Redisplay weather if data exists
        if self.current_weather_data:
            self.page.run_task(self.redisplay_weather)
    
    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
        
        # Add theme switcher
        self.page.theme_mode = ft.ThemeMode.SYSTEM  # Use system theme
        
        # Custom theme Colors
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE,
        )
        
        self.page.padding = 20
        
        # Window properties are accessed via page.window object in Flet 0.28.3
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.window.resizable = False
        self.page.window.center()
    
    def build_ui(self):
        """Build the user interface."""
        # Title
        self.title = ft.Text(
            "Weather App",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700,
        )
        
        # Theme toggle button
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Toggle theme",
            on_click=self.toggle_theme,
        )
        
        # Unit toggle button
        self.unit_toggle = ft.ElevatedButton(
            text="°F" if self.current_unit == "metric" else "°C",
            tooltip="Toggle temperature unit",
            on_click=self.toggle_units,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_600,
            ),
        )

        # Update the Column to include both buttons in the title row
        title_row = ft.Row(
            [
                self.title,
                ft.Row(
                    [
                        self.unit_toggle,
                        self.theme_button,
                    ],
                    spacing=10,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        # City input field
        self.city_input = ft.TextField(
            label="Enter city name",
            hint_text="e.g., London, Tokyo, New York",
            border_color=ft.Colors.BLUE_400,
            icon=ft.Icons.LOCATION_CITY,
            autofocus=True,
            on_submit=self.on_search,
        )
        
        # Search History Dropdown
        self.history_dropdown = ft.Dropdown(
            label="Recent Searches",
            hint_text="Select from history",
            border_color=ft.Colors.BLUE_300,
            icon=ft.Icons.HISTORY,
            on_change=self.on_history_select,
            visible=len(self.search_history) > 0,
            options=[ft.dropdown.Option(city) for city in self.search_history],
        )
        
        # Search button
        self.search_button = ft.ElevatedButton(
            "Get Weather",
            icon=ft.Icons.SEARCH,
            on_click=self.on_search,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
            ),
        )
        
        # Weather display container (initially hidden)
        self.weather_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=20,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )
        
        # Error message
        self.error_message = ft.Text(
            "",
            color=ft.Colors.RED_700,
            visible=False,
        )
        
        # Loading indicator
        self.loading = ft.ProgressRing(visible=False)
        
        # Add all components to page
        self.page.add(
            ft.Column(
                [
                    title_row,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.city_input,
                    self.history_dropdown,
                    self.search_button,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.loading,
                    self.error_message,
                    self.weather_container,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
        )

    def toggle_theme(self, e):
        """Toggle between light and dark theme."""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE
        self.page.update()

    def on_search(self, e):
        """Handle search button click or enter key press."""
        self.page.run_task(self.get_weather)

    async def get_weather(self):
        """Fetch and display weather data."""
        city = self.city_input.value.strip()
        
        # Validate input
        if not city:
            self.show_error("Please enter a city name")
            return
        
        # Show loading, hide previous results
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.page.update()
        
        try:
            # Fetch weather data
            weather_data = await self.weather_service.get_weather(city)
            
            # Store current weather data for unit conversion
            self.current_weather_data = weather_data
            
            # Add to search history on successful fetch
            self.add_to_history(city)
            
            # Display weather
            await self.display_weather(weather_data)
            
        except Exception as e:
            self.show_error(str(e))
        
        finally:
            self.loading.visible = False
            self.page.update()

    async def redisplay_weather(self):
        """Redisplay weather with updated units (no fade animation)."""
        if self.current_weather_data:
            await self.display_weather(self.current_weather_data, animate=False)

    async def display_weather(self, data: dict, animate=True):
        """Display weather information."""
        # Extract data
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp_celsius = data.get("main", {}).get("temp", 0)
        feels_like_celsius = data.get("main", {}).get("feels_like", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        weather_main = data.get("weather", [{}])[0].get("main", "Clear")
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)
        
        # Convert temperatures based on user preference
        temp = self.convert_temp(temp_celsius)
        feels_like = self.convert_temp(feels_like_celsius)
        temp_symbol = self.get_temp_symbol()
        
        # Get weather-specific colors and emoji
        weather_theme = self.get_weather_colors(weather_main, icon_code)
        
        # Build weather display
        self.weather_container.content = ft.Column(
            [
                # Weather emoji at the top
                ft.Text(
                    weather_theme['emoji'],
                    size=60,
                ),
                
                # Location
                ft.Text(
                    f"{city_name}, {country}",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=weather_theme['accent'],
                ),
                
                # Weather icon and description
                ft.Row(
                    [
                        ft.Image(
                            src=f"https://openweathermap.org/img/wn/{icon_code}@2x.png",
                            width=100,
                            height=100,
                        ),
                        ft.Text(
                            description,
                            size=20,
                            italic=True,
                            color=weather_theme['accent'],
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                
                # Temperature
                ft.Text(
                    f"{temp:.1f}{temp_symbol}",
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    color=weather_theme['accent'],
                ),
                
                ft.Text(
                    f"Feels like {feels_like:.1f}{temp_symbol}",
                    size=16,
                    color=ft.Colors.GREY_700,
                ),
                
                ft.Divider(),
                
                # Additional info
                ft.Row(
                    [
                        self.create_info_card(
                            ft.Icons.WATER_DROP,
                            "Humidity",
                            f"{humidity}%",
                            weather_theme['accent']
                        ),
                        self.create_info_card(
                            ft.Icons.AIR,
                            "Wind Speed",
                            f"{wind_speed} m/s",
                            weather_theme['accent']
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        
        # Update container colors with smooth transition
        self.weather_container.bgcolor = weather_theme['bg']
        self.weather_container.gradient = ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=[
                weather_theme['gradient_start'],
                weather_theme['gradient_end'],
            ],
        )
        
        # Animate appearance only if requested
        if animate:
            self.weather_container.animate_opacity = 300
            self.weather_container.opacity = 0
            self.weather_container.visible = True
            self.page.update()

            # Fade in
            import asyncio
            await asyncio.sleep(0.1)
            self.weather_container.opacity = 1
        else:
            self.weather_container.visible = True
        
        self.error_message.visible = False
        self.page.update()

    def create_info_card(self, icon, label, value, accent_color):
        """Create an info card for weather details."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=30, color=accent_color),
                    ft.Text(label, size=12, color=ft.Colors.GREY_600),
                    ft.Text(
                        value,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=accent_color,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=15,
            width=150,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            ),
        )

    def show_error(self, message: str):
        """Display error message."""
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.page.update()


def main(page: ft.Page):
    """Main entry point."""
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)