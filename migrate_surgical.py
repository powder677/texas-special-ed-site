import os

def surgical_migration():
    source_base = './districts_updated'
    target_base = './districts'
    
    # Exact tags based on your snippet
    START_TAG = '<div class="free-resources-section">'
    END_TAG = ''
    
    if not os.path.exists(source_base):
        print(f"❌ Source folder '{source_base}' not found.")
        return

    migrated_count = 0

    for folder_name in os.listdir(source_base):
        source_folder = os.path.join(source_base, folder_name)
        
        # Ensure it's a directory
        if os.path.isdir(source_folder):
            source_file = os.path.join(source_folder, 'partners.html')
            target_file = os.path.join(target_base, folder_name, 'partners.html')
            
            # If both the generated file and the live target file exist
            if os.path.exists(source_file) and os.path.exists(target_file):
                
                # 1. Read the corrupted source file
                with open(source_file, 'r', encoding='utf-8') as f:
                    source_content = f.read()
                    
                # 2. Extract the Free Resources block without using regex
                start_idx = source_content.find(START_TAG)
                end_idx = source_content.find(END_TAG, start_idx)
                
                if start_idx != -1 and end_idx != -1:
                    # Slice out the exact block including the end comment
                    resource_block = source_content[start_idx:end_idx + len(END_TAG)]
                    
                    # 3. Read the clean, live target file
                    with open(target_file, 'r', encoding='utf-8') as f:
                        target_content = f.read()
                        
                    # 4. Inject the block into the target file
                    if START_TAG not in target_content:
                        # Try to inject before closing main tag
                        inject_idx = target_content.find('</main>')
                        
                        # Fallback: if no </main> exists, inject before the footer
                        if inject_idx == -1:
                            inject_idx = target_content.find('<footer')
                            
                        # Fallback 2: inject before body closes
                        if inject_idx == -1:
                            inject_idx = target_content.find('</body>')
                            
                        if inject_idx != -1:
                            # Drop the resources block right into the safe spot
                            new_target_content = target_content[:inject_idx] + "\n" + resource_block + "\n\n" + target_content[inject_idx:]
                            
                            # Save the updated target file
                            with open(target_file, 'w', encoding='utf-8') as f:
                                f.write(new_target_content)
                            migrated_count += 1
                        else:
                            print(f"⚠️ Could not find a safe injection point in {target_file}")
                # Note: We fail silently if the source file doesn't have the block, as it may be empty

    print(f"✅ Surgical Migration Complete! Safely injected resources into {migrated_count} live partner pages.")

if __name__ == '__main__':
    surgical_migration()