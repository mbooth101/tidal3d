#include "py/runtime.h"
#include <math.h>

// Pre-computed PI over 180
#define DEGS_TO_RADS (0.017453)

// Helper to calculate vector magnitude used by v_magnitude and v_normalise
STATIC mp_float_t magnitude(mp_obj_t *vec, size_t len) {
	mp_float_t sum = 0;
	for (size_t i = 0; i < len; i++) {
		mp_float_t f = mp_obj_get_float(vec[i]);
		sum += f * f;
	}
	return sqrt(sum);
}

/**
 * Returns the magnitude (length) of the given vector as a scalar value
 */
STATIC mp_obj_t v_magnitude(mp_obj_t vector) {
	size_t len;
	mp_obj_t *vec;
	mp_obj_get_array(vector, &len, &vec);

	return mp_obj_new_float(magnitude(vec, len));
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(v_magnitude_obj, v_magnitude);

/**
 * Returns the given vector normalised to unit length
 */
STATIC mp_obj_t v_normalise(mp_obj_t vector) {
	size_t len;
	mp_obj_t *vec;
	mp_obj_get_array(vector, &len, &vec);

	mp_float_t mag = magnitude(vec, len);

	mp_obj_list_t *result = MP_OBJ_TO_PTR(mp_obj_new_list(len, NULL));
	for (size_t i = 0; i < len; i++) {
		mp_float_t f = mp_obj_get_float(vec[i]);
		// Avoid divide by zero on zero-length vectors
		if (mag == 0) {
			result->items[i] = mp_obj_new_float(f);
		} else {
			result->items[i] = mp_obj_new_float(f / mag);
		}
	}
	return MP_OBJ_FROM_PTR(result);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(v_normalise_obj, v_normalise);

/**
 * Returns the given vector scaled by the given factor
 */
STATIC mp_obj_t v_scale(mp_obj_t vector, mp_obj_t factor) {
	size_t len;
	mp_obj_t *vec;
	mp_obj_get_array(vector, &len, &vec);

	mp_float_t f = mp_obj_get_float(factor);

	mp_obj_list_t *result = MP_OBJ_TO_PTR(mp_obj_new_list(len, NULL));
	for (size_t i = 0; i < len; i++) {
		result->items[i] = mp_obj_new_float(mp_obj_get_float(vec[i]) * f);
	}
	return MP_OBJ_FROM_PTR(result);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(v_scale_obj, v_scale);

/**
 * Returns the vector given by the sum of the given vectors
 */
STATIC mp_obj_t v_add(mp_obj_t vector1, mp_obj_t vector2) {
	size_t len1, len2;
	mp_obj_t *vec1, *vec2;
	mp_obj_get_array(vector1, &len1, &vec1);
	mp_obj_get_array(vector2, &len2, &vec2);

	size_t len = (len1 < len2 ? len1 : len2);
	mp_obj_list_t *result = MP_OBJ_TO_PTR(mp_obj_new_list(len, NULL));
	for (size_t i = 0; i < len; i++) {
		result->items[i] = mp_obj_new_float(mp_obj_get_float(vec1[i]) + mp_obj_get_float(vec2[i]));
	}
	return MP_OBJ_FROM_PTR(result);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(v_add_obj, v_add);

/**
 * Returns the vector given by subtracting the second vector from the first vector
 */
STATIC mp_obj_t v_subtract(mp_obj_t vector1, mp_obj_t vector2) {
	size_t len1, len2;
	mp_obj_t *vec1, *vec2;
	mp_obj_get_array(vector1, &len1, &vec1);
	mp_obj_get_array(vector2, &len2, &vec2);

	size_t len = (len1 < len2 ? len1 : len2);
	mp_obj_list_t *result = MP_OBJ_TO_PTR(mp_obj_new_list(len, NULL));
	for (size_t i = 0; i < len; i++) {
		result->items[i] = mp_obj_new_float(mp_obj_get_float(vec1[i]) - mp_obj_get_float(vec2[i]));
	}
	return MP_OBJ_FROM_PTR(result);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(v_subtract_obj, v_subtract);

/**
 * Returns the vector that is the average of the list of given vectors, although this can be
 * expressed as a composition of v_add and v_scale, this common operation is much quicker done
 * as a single call
 */
STATIC mp_obj_t v_average(mp_obj_t vectors) {
	size_t list_len;
	mp_obj_t *list;
	mp_obj_get_array(vectors, &list_len, &list);

	mp_float_t x = 0, y = 0, z = 0;

	mp_obj_t *vec;
	for (size_t i = 0; i < list_len; i++) {
		mp_obj_get_array_fixed_n(list[i], 3, &vec);
		x += mp_obj_get_float(vec[0]);
		y += mp_obj_get_float(vec[1]);
		z += mp_obj_get_float(vec[2]);
	}

	mp_obj_list_t *result = MP_OBJ_TO_PTR(mp_obj_new_list(3, NULL));
	result->items[0] = mp_obj_new_float(x / list_len);
	result->items[1] = mp_obj_new_float(y / list_len);
	result->items[2] = mp_obj_new_float(z / list_len);
	return MP_OBJ_FROM_PTR(result);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(v_average_obj, v_average);

/**
 * Returns the vector given by multiplying the given vector by the given matrix
 */
STATIC mp_obj_t v_multiply(mp_obj_t vector, mp_obj_t matrix) {
	mp_obj_t *vec;
	mp_obj_get_array_fixed_n(vector, 3, &vec);
	mp_float_t x = mp_obj_get_float(vec[0]);
	mp_float_t y = mp_obj_get_float(vec[1]);
	mp_float_t z = mp_obj_get_float(vec[2]);

	size_t mat_len;
	mp_obj_t *mat;
	mp_obj_get_array(matrix, &mat_len, &mat);
	if (mat_len < 4) {
		mp_raise_ValueError(MP_ERROR_TEXT("matrix must be length 4"));
	}
	mp_obj_t *m0, *m1, *m2, *m3;
	mp_obj_get_array(mat[0], &mat_len, &m0);
	mp_obj_get_array(mat[1], &mat_len, &m1);
	mp_obj_get_array(mat[2], &mat_len, &m2);
	mp_obj_get_array(mat[3], &mat_len, &m3);

	float xyzw[4];
	for (size_t i = 0; i < 4; i++) {
		xyzw[i] = x * mp_obj_get_float(m0[i])
			+ y * mp_obj_get_float(m1[i])
			+ z * mp_obj_get_float(m2[i])
			+ mp_obj_get_float(m3[i]);
	}

	mp_obj_list_t *result = MP_OBJ_TO_PTR(mp_obj_new_list(3, NULL));
	result->items[0] = mp_obj_new_float(xyzw[0] / xyzw[3]);
	result->items[1] = mp_obj_new_float(xyzw[1] / xyzw[3]);
	result->items[2] = mp_obj_new_float(xyzw[2] / xyzw[3]);
	return MP_OBJ_FROM_PTR(result);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(v_multiply_obj, v_multiply);

/**
 * Returns a scalar value of 0 if the given vectors are exactly perpendicular, <0 if the angle
 * between them is greater than 90° or >0 if the angle between them is less than 90° (dot product)
 */
STATIC mp_obj_t v_dot(mp_obj_t vector1, mp_obj_t vector2) {
	size_t len1, len2;
	mp_obj_t *v1, *v2;
	mp_obj_get_array(vector1, &len1, &v1);
	mp_obj_get_array(vector2, &len2, &v2);

	mp_float_t result = 0;
	for (size_t i = 0; i < (len1 < len2 ? len1 : len2); i++) {
		mp_float_t a = mp_obj_get_float(v1[i]);
		mp_float_t b = mp_obj_get_float(v2[i]);
		result += a * b;
	}
	return mp_obj_new_float(result);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(v_dot_obj, v_dot);

/**
 * Returns the vector that is exactly perpendicular to both the given vectors (cross product)
 */
STATIC mp_obj_t v_cross(mp_obj_t vector1, mp_obj_t vector2) {
	size_t len1, len2;
	mp_obj_t *vec1, *vec2;
	mp_obj_get_array(vector1, &len1, &vec1);
	mp_obj_get_array(vector2, &len2, &vec2);

	size_t len = (len1 < len2 ? len1 : len2);
	mp_obj_list_t *result = MP_OBJ_TO_PTR(mp_obj_new_list(len, NULL));
	for (size_t i = 0, n = 0, nn = 0; i < len; i++) {
		n = (i + 1) % len;
		nn = (i + 2) % len;
		mp_float_t val = mp_obj_get_float(vec1[n]) * mp_obj_get_float(vec2[nn]) -
				 mp_obj_get_float(vec1[nn]) * mp_obj_get_float(vec2[n]);
		result->items[i] = mp_obj_new_float(val);
	}
	return MP_OBJ_FROM_PTR(result);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(v_cross_obj, v_cross);

/**
 * Return screen coordinates for a list of vectors containing normalised device coordinates (NDCs),
 * an NDC with x and y values of between -1.0 and 1.0 are mapped to valid screen coordinates within
 * the contraints of the given screen dimensions in pixels
 */
STATIC mp_obj_t v_ndc_to_screen(mp_obj_t vectors, mp_obj_t width, mp_obj_t height) {
	size_t list_len;
	mp_obj_t *vecs, *vec;
	mp_obj_get_array(vectors, &list_len, &vecs);

	mp_float_t w = mp_obj_get_float(width);
	mp_float_t h = mp_obj_get_float(height);

	mp_obj_list_t *result = MP_OBJ_TO_PTR(mp_obj_new_list(list_len * 2, NULL));

	for (size_t i = 0; i < list_len; i++) {
		mp_obj_get_array_fixed_n(vecs[i], 3, &vec);

		mp_float_t x = (mp_obj_get_float(vec[0]) + 1) * 0.5 * w;
		mp_float_t y = (1 - (mp_obj_get_float(vec[1]) + 1) * 0.5) * h;

		result->items[i * 2] = mp_obj_new_int(x);
		result->items[i * 2 + 1] = mp_obj_new_int(y);
	}

	return MP_OBJ_FROM_PTR(result);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_3(v_ndc_to_screen_obj, v_ndc_to_screen);

/**
 * Returns the matrix given by multiplying together the two given 4x4 matrices
 */
STATIC mp_obj_t m_multiply(mp_obj_t matrix1, mp_obj_t matrix2) {
	mp_obj_t *mat1, *mat2;
	mp_obj_get_array_fixed_n(matrix1, 16, &mat1);
	mp_obj_get_array_fixed_n(matrix2, 16, &mat2);

	// We are assuming here that both operands are 4x4 matrices, but you could make these loops work
	// for multiplying arbitrarily sized matrices if the number of rows on the LHS is equal to the
	// number of columns on the RHS
	mp_obj_list_t *result = MP_OBJ_TO_PTR(mp_obj_new_list(16, NULL));
	for (size_t i = 0; i < 4; i++) { // Num of rows on the LHS
		for (size_t j = 0; j < 4; j++) { // Num of cols on the RHS
			mp_float_t val = 0;
			val += mp_obj_get_float(mat1[i * 4 + 0]) * mp_obj_get_float(mat2[0 + j]);
			val += mp_obj_get_float(mat1[i * 4 + 1]) * mp_obj_get_float(mat2[4 + j]);
			val += mp_obj_get_float(mat1[i * 4 + 2]) * mp_obj_get_float(mat2[8 + j]);
			val += mp_obj_get_float(mat1[i * 4 + 3]) * mp_obj_get_float(mat2[12 + j]);
			result->items[i * 4 + j] = mp_obj_new_float(val);
		}
	}
	return MP_OBJ_FROM_PTR(result);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(m_multiply_obj, m_multiply);

/**
 * Returns the matrix given by translating the given 4x4 matrix by the given 3D vector
 */
STATIC mp_obj_t m_translate(mp_obj_t matrix, mp_obj_t vector) {
	mp_obj_t *vec;
	mp_obj_get_array_fixed_n(vector, 3, &vec);

	mp_obj_list_t *trans_mat = MP_OBJ_TO_PTR(mp_obj_new_list(16, NULL));
	for (size_t i = 0; i < 4; i++) {
		for (size_t j = 0; j < 4; j++) {
			if (i == j) {
				trans_mat->items[i * 4 + j] = mp_obj_new_float(1);
			} else {
				trans_mat->items[i * 4 + j] = mp_obj_new_float(0);
			}
		}
	}
	trans_mat->items[12] = mp_obj_new_float(mp_obj_get_float(vec[0]));
	trans_mat->items[13] = mp_obj_new_float(mp_obj_get_float(vec[1]));
	trans_mat->items[14] = mp_obj_new_float(mp_obj_get_float(vec[2]));
	return m_multiply(matrix, MP_OBJ_FROM_PTR(trans_mat));
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(m_translate_obj, m_translate);

/**
 * Returns the matrix given by rotating the given 4x4 matrix by the given quaternion
 */
STATIC mp_obj_t m_rotate(mp_obj_t matrix, mp_obj_t quaternion) {
	mp_obj_t *quat;
	mp_obj_get_array_fixed_n(quaternion, 4, &quat);
	mp_float_t w = mp_obj_get_float(quat[0]);
	mp_float_t x = mp_obj_get_float(quat[1]);
	mp_float_t y = mp_obj_get_float(quat[2]);
	mp_float_t z = mp_obj_get_float(quat[3]);

	mp_obj_list_t *rot_mat = MP_OBJ_TO_PTR(mp_obj_new_list(16, NULL));
	rot_mat->items[0] = mp_obj_new_float(1 - 2 * (y * y + z * z));
	rot_mat->items[1] = mp_obj_new_float(2 * (x * y - w * z));
	rot_mat->items[2] = mp_obj_new_float(2 * (x * z + w * y));
	rot_mat->items[3] = mp_obj_new_float(0);
	rot_mat->items[4] = mp_obj_new_float(2 * (x * y + w * z));
	rot_mat->items[5] = mp_obj_new_float(1 - 2 * (x * x + z * z));
	rot_mat->items[6] = mp_obj_new_float(2 * (y * z - w * x));
	rot_mat->items[7] = mp_obj_new_float(0);
	rot_mat->items[8] = mp_obj_new_float(2 * (x * z - w * y));
	rot_mat->items[9] = mp_obj_new_float(2 * (y * z + w * x));
	rot_mat->items[10] = mp_obj_new_float(1 - 2 * (x * x + y * y));
	rot_mat->items[11] = mp_obj_new_float(0);
	rot_mat->items[12] = mp_obj_new_float(0);
	rot_mat->items[13] = mp_obj_new_float(0);
	rot_mat->items[14] = mp_obj_new_float(0);
	rot_mat->items[15] = mp_obj_new_float(1);
	return m_multiply(matrix, MP_OBJ_FROM_PTR(rot_mat));
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(m_rotate_obj, m_rotate);

/**
 * Returns the quaternion given by rotating the given quaternion by the given number of degrees
 * around the axis described by the given 3D vector
 */
STATIC mp_obj_t q_rotate(mp_obj_t quaternion, mp_obj_t degrees, mp_obj_t vector) {
	mp_obj_t *vec, *quat;

	mp_obj_get_array_fixed_n(quaternion, 4, &quat);
	mp_obj_get_array_fixed_n(vector, 3, &vec);

	mp_float_t q1w = mp_obj_get_float(quat[0]);
	mp_float_t q1x = mp_obj_get_float(quat[1]);
	mp_float_t q1y = mp_obj_get_float(quat[2]);
	mp_float_t q1z = mp_obj_get_float(quat[3]);

	// Compute a rotation quaternion from the angle and vector
	mp_float_t theta = (mp_obj_get_float(degrees) * DEGS_TO_RADS) / 2;
	mp_float_t factor = sin(theta);
	mp_float_t q2w = cos(theta);
	mp_float_t q2x = mp_obj_get_float(vec[0]) * factor;
	mp_float_t q2y = mp_obj_get_float(vec[1]) * factor;
	mp_float_t q2z = mp_obj_get_float(vec[2]) * factor;

	// Multiply the given quaternion by the rotation quaternion
	mp_obj_list_t *result = MP_OBJ_TO_PTR(mp_obj_new_list(4, NULL));
	result->items[0] = mp_obj_new_float(q1w * q2w - q1x * q2x - q1y * q2y - q1z * q2z);
	result->items[1] = mp_obj_new_float(q1w * q2x + q1x * q2w + q1y * q2z - q1z * q2y);
	result->items[2] = mp_obj_new_float(q1w * q2y - q1x * q2z + q1y * q2w + q1z * q2x);
	result->items[3] = mp_obj_new_float(q1w * q2z + q1x * q2y - q1y * q2x + q1z * q2w);
	return MP_OBJ_FROM_PTR(result);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_3(q_rotate_obj, q_rotate);

#if !MICROPY_ENABLE_DYNRUNTIME
STATIC const mp_rom_map_elem_t tidal3d_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_tidal3d) },
    { MP_ROM_QSTR(MP_QSTR_v_magnitude), MP_ROM_PTR(&v_magnitude_obj) },
    { MP_ROM_QSTR(MP_QSTR_v_normalise), MP_ROM_PTR(&v_normalise_obj) },
    { MP_ROM_QSTR(MP_QSTR_v_scale), MP_ROM_PTR(&v_scale_obj) },
    { MP_ROM_QSTR(MP_QSTR_v_add), MP_ROM_PTR(&v_add_obj) },
    { MP_ROM_QSTR(MP_QSTR_v_subtract), MP_ROM_PTR(&v_subtract_obj) },
    { MP_ROM_QSTR(MP_QSTR_v_average), MP_ROM_PTR(&v_average_obj) },
    { MP_ROM_QSTR(MP_QSTR_v_multiply), MP_ROM_PTR(&v_multiply_obj) },
    { MP_ROM_QSTR(MP_QSTR_v_dot), MP_ROM_PTR(&v_dot_obj) },
    { MP_ROM_QSTR(MP_QSTR_v_cross), MP_ROM_PTR(&v_cross_obj) },
    { MP_ROM_QSTR(MP_QSTR_v_ndc_to_screen), MP_ROM_PTR(&v_ndc_to_screen_obj) },
    { MP_ROM_QSTR(MP_QSTR_m_multiply), MP_ROM_PTR(&m_multiply_obj) },
    { MP_ROM_QSTR(MP_QSTR_m_translate), MP_ROM_PTR(&m_translate_obj) },
    { MP_ROM_QSTR(MP_QSTR_m_rotate), MP_ROM_PTR(&m_rotate_obj) },
    { MP_ROM_QSTR(MP_QSTR_q_rotate), MP_ROM_PTR(&q_rotate_obj) },
};
STATIC MP_DEFINE_CONST_DICT(tidal3d_module_globals, tidal3d_module_globals_table);

const mp_obj_module_t tidal3d_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&tidal3d_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_tidal3d, tidal3d_module);
#endif
