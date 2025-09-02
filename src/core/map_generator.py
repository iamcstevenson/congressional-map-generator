"""Mobile-first congressional district map generator"""

import folium
import json
from pathlib import Path
import argparse
import sys

class DistrictMapGenerator:
    """Generate mobile-optimized district maps"""
    
    def __init__(self, district_code: str = "KY-06"):
        self.district_code = district_code
        self.district_boundary = self._load_district_boundary()
        
    def _load_district_boundary(self):
        """Load district boundary from GeoJSON"""
        boundary_path = Path(f"data/boundaries/{self.district_code.lower().replace('-', '_')}/boundary_simplified.geojson")
        if not boundary_path.exists():
            boundary_path = Path(f"data/boundaries/{self.district_code.lower().replace('-', '_')}/boundary.geojson")
        
        if not boundary_path.exists():
            raise FileNotFoundError(f"Boundary file not found for {self.district_code}")
        
        with open(boundary_path, 'r') as f:
            return json.load(f)
    
    def generate_map(self, title: str = "KY-06 Congressional District"):
        """Generate basic map"""
        # Get the geometry
        if 'features' in self.district_boundary and self.district_boundary['features']:
            geometry = self.district_boundary['features'][0]['geometry']
            coords = geometry['coordinates'][0] if geometry['type'] == 'Polygon' else geometry['coordinates'][0][0]
            
            # Calculate center from coordinates
            lons = [c[0] for c in coords]
            lats = [c[1] for c in coords]
            center_lon = sum(lons) / len(lons)
            center_lat = sum(lats) / len(lats)
        else:
            # Default center for KY-06 (Lexington area)
            center_lat, center_lon = 38.0406, -84.5037
        
        # Create map with mobile-friendly settings
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=9,
            max_zoom=18,
            min_zoom=7,
            tiles='CartoDB positron',
            prefer_canvas=True
        )
        
        # Add district boundary
        style = {
            'fillColor': '#3498db',
            'fillOpacity': 0.15,
            'color': '#2c3e50',
            'weight': 3,
            'dashArray': '5, 5'
        }
        
        folium.GeoJson(
            self.district_boundary,
            name=f"{self.district_code} Boundary",
            style_function=lambda x: style,
            tooltip=folium.Tooltip(f"<b>{self.district_code}</b>", sticky=True)
        ).add_to(m)
        
        # Add mobile-friendly title
        title_html = f'''
        <div style="
            position: fixed;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(255, 255, 255, 0.95);
            padding: 10px 20px;
            border-radius: 5px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            z-index: 1000;
            font-weight: 600;
            font-size: 18px;
            color: #2c3e50;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        ">{title}</div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Add mobile zoom controls
        zoom_html = '''
        <div style="position: fixed; bottom: 20px; right: 20px; z-index: 1000;">
            <button onclick="document.querySelector('.leaflet-container').leafletMap.zoomIn()" style="
                width: 50px; height: 50px; 
                background: white; border: 2px solid #ccc;
                border-radius: 5px; font-size: 24px;
                margin-bottom: 10px; display: block;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                cursor: pointer;
                -webkit-tap-highlight-color: rgba(0,0,0,0);
                user-select: none;
            ">+</button>
            <button onclick="document.querySelector('.leaflet-container').leafletMap.zoomOut()" style="
                width: 50px; height: 50px;
                background: white; border: 2px solid #ccc;
                border-radius: 5px; font-size: 24px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                cursor: pointer;
                -webkit-tap-highlight-color: rgba(0,0,0,0);
                user-select: none;
            ">−</button>
        </div>
        
        <script>
            window.addEventListener('load', function() {
                var mapContainers = document.querySelectorAll('.leaflet-container');
                if (mapContainers.length > 0) {
                    mapContainers[0].leafletMap = window[Object.keys(window).find(key => key.startsWith('map_'))];
                }
            });
        </script>
        '''
        m.get_root().html.add_child(folium.Element(zoom_html))
        
        return m
    
    def save_map(self, map_obj, output_path: str = "outputs/map.html"):
        """Save map to HTML file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        map_obj.save(str(output_path))
        print(f"✓ Map saved to {output_path}")
        return output_path

def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(description='Generate congressional district map')
    parser.add_argument('--district', default='KY-06', help='District code')
    parser.add_argument('--title', default='KY-06 Congressional District', help='Map title')
    parser.add_argument('--output', default='outputs/map.html', help='Output path')
    
    args = parser.parse_args()
    
    try:
        generator = DistrictMapGenerator(args.district)
        map_obj = generator.generate_map(args.title)
        generator.save_map(map_obj, args.output)
        print(f"✓ Successfully generated map for {args.district}")
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
