joint_profile_pin_spacing = (2, 400, 0.1)  # min, max, step
joint_profile_depth = (2, 20, 0.1)
joint_profile_bit_height = (2, 20, 0.1)
joint_profile_bit_width = (2, 24, 0.1)
joint_profile_distance_from_bottom = (2, 100, 0.1)
joint_profile_material_thickness = (6, 26, 0.1)
bit_to_use = (1, 100, 0)  # this needs to be from the bits that are added to the bit profiles


dowel_profile_edge_depth = (2, 35, 0.1)
dowel_profile_face_depth = (2, 25, 0.1)
dowel_profile_dis_from_face = (2, 25, 0.1)
dowel_profile_dis_from_edge = (2, 100, 0.1)
dowel_profile_spacing = (2, 400, 0.1)
joint_deep_adjustment = (-2, 2, .01)
joint_tightness_adjustment = (-2, 2, .01)
bit_profile_number = (1, 100, 1)
bit_profile_angle = (0, 15, 0.1)
bit_profile_diameter = (1, 25, 1)
bit_profile_cutting_edge_length = (1, 50, 1)
bit_profile_number_of_flutes = (1, 4, 1)
bit_profile_feed_speed = (1, 20000, 1)
bit_profile_spindle_speed = (1, 24000, 1) # this is only allowing 944.882 rpm

spindle_time_out = (2, 240, 1)

# sanding
part_stile_width = (2, 20, 0.1)
part_profile_width = (2, 20, 0.1)
part_profile_panel_width = (2, 24, 0.1)

# sanding paper
sanding_grit_range = (36, 400, 1)
sanding_feed_speed = (1, 24000, 1)  # this is only allowing 944.882 rpm
distance_to_edge_of_sandpaper = (2, 24, 0.1)
sandpaper_distance_to_edge_of_profile = (2, 24, 0.1)
sanding_pressure = (0, 10, 1)
sanding_hold_back_from_edges = (0, 10, 0.5)
sandpaper_overhang = (0, 40, 5)
sandpaper_Overlap = (0, 100, 10)
sandpaper_speed = (10, 100, 10)

# door styles
door_styles_outside_edge_width = (0, 610, 1)
door_styles_inside_edge_width = (0, 610, 1)
door_styles_frame_width = (1, 610, 1)
door_styles_hold_back_from_edges = (0, 10, 0.5)

# dovetail setting ranges
dovetail_setting_standard_width_1 = (1, 610, 1)
dovetail_setting_standard_width_2 = (1, 610, 1)
dovetail_setting_standard_width_3 = (1, 610, 1)
dovetail_setting_standard_width_4 = (1, 610, 1)

dovetail_setting_x_zero = (0, 200, 0.1)
dovetail_setting_y_zero = (0, 200, 0.1)
dovetail_setting_z_zero = (-20, 10, 0.1)
dovetail_setting_a_zero = (1, 100, 0.1)
dovetail_setting_b_zero = (1, 100, 0.1)
dovetail_fence_distance = (457.2, 609.6, 0.01)

# Sander Range
sander_x_length = (1, 610, 1)
sander_y_length = (1, 610, 1)
sander_x_zero = (0, 900, 0.1)
