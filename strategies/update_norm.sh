#!/bin/bash
# Script to update remaining normalization patterns in strategy files

# Function to update a single file
update_file() {
    local file=$1
    echo "Updating $file..."
    
    # Add import if not present
    if ! grep -q "from strategies.utils import normalize_confidence" "$file"; then
        # Find the last strategies.* import and add after it
        sed -i '/^from strategies\./,/^$/ {
            /^from strategies\./ {
                n
                /^$/ {
                    i\
from strategies.utils import normalize_confidence

                }
            }
        }' "$file"
    fi
    
    # Replace normalization patterns
    # Pattern: (value - min) / (max - min) if max != min else default
    sed -i 's/(\([^ ]*\) - \([^ ]*\)) \/ (\([^ ]*\) - \([^ ]*\)) if \([^ ]*\) != \([^ ]*\) else \([^ ]*\)/normalize_confidence(\1, \2, \3)/g' "$file"
    
    # Pattern: value / divisor if divisor != 0 else default
    sed -i 's/\([^ ]*\) \/ \([^ ]*\) if \([^ ]*\) != 0 else \([^ ]*\)/normalize_confidence(\1, 0, \2)/g' "$file"
}

# Update remaining files
for file in full_data/iv_skew_squeeze.py full_data/prob_distribution_shift.py layer1/gamma_wall_bounce.py layer1/gex_imbalance.py layer1/vol_compression_range.py layer2/delta_gamma_squeeze.py layer3/strike_concentration.py; do
    if [ -f "$file" ]; then
        update_file "$file"
    fi
done

echo "Done!"
