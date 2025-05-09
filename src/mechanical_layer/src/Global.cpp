/*
    Copyright 2025 <Dufour Oscar, Maxime Stappel, David Rodney, Nicolas Alexandre, Institute of Light and Matter, CNRS UMR 5306>
    Global variables, operators and function used by the whole library.
 */

#include "Global.h"

#include <string>
#include <utility>
#include <vector>
using std::map, std::string, std::vector, std::pair, std::stringstream;

/*
    Operations on new types: definitions
 */
/*  Define operations on type double2  */
//  Addition of two double2 vectors
double2 operator+(double2 const& a, double2 const& b) { return {a.first + b.first, a.second + b.second}; }
double2 operator-(double2 const& a, double2 const& b) { return {a.first - b.first, a.second - b.second}; }
//  Element-wise multiplication
double2 operator*(double2 const& a, double2 const& b) { return {a.first * b.first, a.second * b.second}; }
//  Scalar multiplication with a double2 vector
double2 operator*(double const coef, double2 const& R) { return {coef * R.first, coef * R.second}; }
//  Dot product
double operator%(double2 const& a, double2 const& b) { return a.first * b.first + a.second * b.second; }
// Norm (magnitude) of a double2 vector
double operator!(double2 const& a) { return sqrt(a % a); }
// Cross product-like operation for 2D vectors (returns perpendicular vector scaled by scalar)
double2 operator^(double const a, double2 const& b) { return {-a * b.second, a * b.first}; }

/*  Define operations on type int2  */
//  Addition of two int2 vectors
int2 operator+(int2 const& a, int2 const& b) { return {a.first + b.first, a.second + b.second}; }
int2 operator-(int2 const& a, int2 const& b) { return {a.first - b.first, a.second - b.second}; }
//  Element-wise multiplication
int2 operator*(int2 const& a, int2 const& b) { return {a.first * b.first, a.second * b.second}; }

/*
    Global variables
                        */
uint32_t nAgents;
map<string, uint32_t> agentMap;   //  Correspondence between user-given ids and internal ids
vector<string> agentMapInverse;   //  Inverse version for output
Agent** agents;                   //  The array of pointers to the agent objects

map<pair<string, string>, uint32_t> shapeMap;   //  Correspondence between user-given Shapeids and internal ids.
vector<string> shapeMapInverse;                 //  We store the couple (Agent id, shape id) in shapeMap, but the
                                                //  inverse map is only used for output, which is done by agent.

//  Geometry
double Lx;
double Ly;
vector<vector<double2>> listObstacles;

//  Basic parameters
double dt;        //  Time step of the main loop.
double dt_mech;   //  Time step of the mechanical layer.

/*  Mechanical layer  */
//  Materials
vector<double2> agentProperties;
uint32_t nMaterials;
double** intrinsicProperties;
double*** binaryProperties;
vector<int32_t> obstaclesMaterial;
map<uint32_t, int32_t> shapesMaterial;

//  Paths
string pathStatic;    //  Folder where the static  data should be saved
string pathDynamic;   //  Folder where the dynamic data should be placed

/*
    Utilities functions
                        */
/**
 * @brief Parses a string containing a pair of doubles.
 *
 * @param line The string to be parsed.
 *
 * @return A vector of doubles containing the parsed values.
 */
pair<int, double2> parse2DComponents(const char* line)
{
    vector<double> result;
    stringstream ss(line);
    string token;
    uint8_t counter = 0;
    while (getline(ss, token, ','))
    {
        double value;
        try
        {
            value = stod(token);
        }
        catch (...)
        {
            return {EXIT_FAILURE, {0., 0.}};
        }
        result.push_back(value);
        counter++;
        if (counter > 2)
            return {EXIT_FAILURE, {0., 0.}};
    }
    return {EXIT_SUCCESS, {result[0], result[1]}};
}

/**
 * @brief Calculates the distance to a wall and the closest point on the wall from a given point.
 *
 * @param vertexA The first vertex of the wall segment.
 * @param vertexB The second vertex of the wall segment.
 * @param C The point for which the distance and closest point are calculated.
 *
 * @return A pair containing the distance to the wall and the closest point on the wall.
 */
pair<double, double2> get_distance_to_wall_and_closest_point(double2 vertexA, double2 vertexB, const double2& C)
{
    const double2 AB = vertexB - vertexA;
    const double2 AC = C - vertexA;
    //  gamma: coefficient such that the closest point P on (AB) satisfies AP= gamma AB
    const double gamma = AB % AC / (AB % AB);

    if (gamma <= 0.0)
        //  Closest point is vertexA
        return make_pair(!AC, double2(vertexA));
    if (gamma >= 1.0)
        //  Closest point is vertexB
        return make_pair(!(C - vertexB), double2(vertexB));

    //  Else: closest point P on (AB) to C
    double2 P = vertexA + gamma * AB;
    return make_pair(!(C - P), double2(P));
}

/**
 * @brief Calculates the interval of a given value within a specified length.
 *
 * The interval is calculated by adding half of the length to the value,
 * taking the modulo of the sum with the length, and subtracting half of the length.
 *
 * @param x The value for which the interval is calculated.
 * @param length The length of the interval.
 *
 * @return The interval of the value within the specified length.
 */
inline double get_interval(const double x, const double length) { return fmod(x + 0.5 * length, length) - 0.5 * length; }

/**
 * Calculates the Euclidean distance between two points in a 2D space lattice.
 *
 * @param A The coordinates of the first point.
 * @param B The coordinates of the second point.
 * @return The Euclidean distance between the two points.
 */
double get_distance(const double2& A, const double2& B)
{
    const double x_mod = get_interval(A.first - B.first, Lx);
    const double y_mod = get_interval(A.second - B.second, Ly);
    return sqrt(pow(x_mod, 2) + pow(y_mod, 2));
}
